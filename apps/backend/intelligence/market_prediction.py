from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from config import settings
from models.schemas import CarPricePredictionRequest

FUEL_TYPE_MAPPING = {
    "Petrol": 0,
    "Diesel": 1,
    "CNG": 2,
}

SELLER_TYPE_MAPPING = {
    "Dealer": 0,
    "Individual": 1,
}

TRANSMISSION_MAPPING = {
    "Manual": 0,
    "Automatic": 1,
}


class PredictionError(RuntimeError):
    pass


class PredictorMisconfiguredError(PredictionError):
    pass


class UnsupportedCategoryError(PredictionError):
    pass


class InvalidPredictionInputError(PredictionError):
    pass


@dataclass(frozen=True)
class CarPricePredictionResult:
    predicted_price: float
    raw_prediction: float
    feature_vector: list[float]
    car_age: int


_runtime_client = None


def _get_runtime_client():
    global _runtime_client
    if _runtime_client is None:
        try:
            import boto3
        except ModuleNotFoundError as exc:
            raise PredictorMisconfiguredError(
                "boto3 is not installed in the backend environment."
            ) from exc

        _runtime_client = boto3.client("sagemaker-runtime", region_name=settings.SAGEMAKER_REGION)
    return _runtime_client


def _encode_category(raw_value: str, mapping: dict[str, int], field_name: str) -> int:
    value = (raw_value or "").strip()
    if value not in mapping:
        supported = ", ".join(mapping.keys())
        raise UnsupportedCategoryError(
            f"Unsupported {field_name} '{raw_value}'. Supported values: {supported}."
        )
    return mapping[value]


def build_feature_vector(body: CarPricePredictionRequest) -> tuple[list[float], int]:
    car_age = settings.CAR_PRICE_MODEL_REFERENCE_YEAR - int(body.Year)
    if car_age < 0:
        raise InvalidPredictionInputError(
            f"Year must be less than or equal to {settings.CAR_PRICE_MODEL_REFERENCE_YEAR}."
        )

    feature_vector = [
        float(body.Present_Price),
        float(body.Kms_Driven),
        float(_encode_category(body.Fuel_Type, FUEL_TYPE_MAPPING, "Fuel_Type")),
        float(_encode_category(body.Seller_Type, SELLER_TYPE_MAPPING, "Seller_Type")),
        float(_encode_category(body.Transmission, TRANSMISSION_MAPPING, "Transmission")),
        float(body.Owner),
        float(car_age),
    ]
    return feature_vector, car_age


def _serialize_csv(feature_vector: list[float]) -> str:
    return ",".join(f"{value:g}" for value in feature_vector)


def _unwrap_prediction(candidate: Any) -> float:
    if isinstance(candidate, (int, float)):
        return float(candidate)

    if isinstance(candidate, str):
        return float(candidate.strip())

    if isinstance(candidate, list):
        if not candidate:
            raise PredictionError("Prediction response list is empty.")
        return _unwrap_prediction(candidate[0])

    if isinstance(candidate, dict):
        for key in ("predictions", "prediction", "score", "predicted_value", "value"):
            if key in candidate:
                return _unwrap_prediction(candidate[key])

    raise PredictionError(f"Unsupported prediction response payload: {candidate!r}")


def _parse_prediction(body_bytes: bytes) -> float:
    payload = body_bytes.decode("utf-8").strip()
    if not payload:
        raise PredictionError("SageMaker endpoint returned an empty response.")

    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError:
        first_value = payload.split(",")[0].strip()
        return float(first_value)

    return _unwrap_prediction(parsed)


def _scale_prediction_to_vnd(raw_prediction: float) -> float:
    return float(raw_prediction) * settings.CAR_PRICE_MODEL_OUTPUT_MULTIPLIER_VND


def predict_car_price(body: CarPricePredictionRequest) -> CarPricePredictionResult:
    if not settings.SAGEMAKER_CAR_PRICE_ENDPOINT_NAME:
        raise PredictorMisconfiguredError(
            "SAGEMAKER_CAR_PRICE_ENDPOINT_NAME is not configured."
        )

    feature_vector, car_age = build_feature_vector(body)
    runtime = _get_runtime_client()

    try:
        response = runtime.invoke_endpoint(
            EndpointName=settings.SAGEMAKER_CAR_PRICE_ENDPOINT_NAME,
            ContentType=settings.SAGEMAKER_CAR_PRICE_CONTENT_TYPE,
            Accept="text/csv",
            Body=_serialize_csv(feature_vector),
        )
    except Exception as exc:
        raise PredictionError(f"Failed to invoke SageMaker endpoint: {exc}") from exc

    raw_prediction = _parse_prediction(response["Body"].read())
    return CarPricePredictionResult(
        predicted_price=_scale_prediction_to_vnd(raw_prediction),
        raw_prediction=raw_prediction,
        feature_vector=feature_vector,
        car_age=car_age,
    )
