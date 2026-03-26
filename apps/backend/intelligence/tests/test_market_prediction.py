import io
import json
import os
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from api.router_market import router
from config import settings
from intelligence import market_prediction
from utils.currency import from_usd_input, to_usd_display


class FakeRuntimeClient:
    def __init__(self, payload: str):
        self.payload = payload
        self.calls = []

    def invoke_endpoint(self, **kwargs):
        self.calls.append(kwargs)
        return {"Body": io.BytesIO(self.payload.encode("utf-8"))}


def test_market_prediction_post_encodes_features(monkeypatch):
    app = FastAPI()
    app.include_router(router, prefix="/api")
    client = TestClient(app)

    fake_runtime = FakeRuntimeClient("123.45")
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_ENDPOINT_NAME", "car-price-endpoint")
    monkeypatch.setattr(settings, "SAGEMAKER_REGION", "us-west-2")
    monkeypatch.setattr(settings, "CAR_PRICE_MODEL_REFERENCE_YEAR", 2026)
    monkeypatch.setattr(settings, "CAR_PRICE_MODEL_OUTPUT_MULTIPLIER_VND", 28_100_000)
    monkeypatch.setattr(market_prediction, "_runtime_client", fake_runtime)

    res = client.post(
        "/api/market/prediction",
        json={
            "Present_Price": 5.5,
            "Kms_Driven": 45000,
            "Fuel_Type": "Diesel",
            "Seller_Type": "Individual",
            "Transmission": "Automatic",
            "Owner": 0,
            "Year": 2020,
        },
    )

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["predicted_price"] == to_usd_display(3_468_945_000.0)
    assert data["data"]["raw_model_prediction"] == 123.45
    assert data["data"]["prediction_unit"] == "USD"
    assert data["data"]["model_input"]["car_age"] == 6
    assert data["data"]["feature_vector"] == [from_usd_input(5.5), 45000.0, 1.0, 1.0, 1.0, 0.0, 6.0]

    call = fake_runtime.calls[0]
    assert call["EndpointName"] == "car-price-endpoint"
    assert call["ContentType"] == "text/csv"
    assert call["Body"] == f"{from_usd_input(5.5):g},45000,1,1,1,0,6"


def test_market_prediction_get_supports_contract_query_params(monkeypatch):
    app = FastAPI()
    app.include_router(router, prefix="/api")
    client = TestClient(app)

    fake_runtime = FakeRuntimeClient('{"predictions":[88.1]}')
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_ENDPOINT_NAME", "car-price-endpoint")
    monkeypatch.setattr(settings, "CAR_PRICE_MODEL_REFERENCE_YEAR", 2026)
    monkeypatch.setattr(settings, "CAR_PRICE_MODEL_OUTPUT_MULTIPLIER_VND", 28_100_000)
    monkeypatch.setattr(market_prediction, "_runtime_client", fake_runtime)

    res = client.get(
        "/api/market/prediction",
        params={
            "Present_Price": 7.8,
            "Kms_Driven": 12000,
            "Fuel_Type": "Petrol",
            "Seller_Type": "Dealer",
            "Transmission": "Manual",
            "Owner": 1,
            "Year": 2024,
        },
    )

    assert res.status_code == 200
    data = res.json()
    assert data["data"]["predicted_price"] == to_usd_display(2_475_610_000.0)
    assert data["data"]["raw_model_prediction"] == 88.1
    assert data["data"]["feature_vector"] == [from_usd_input(7.8), 12000.0, 0.0, 0.0, 0.0, 1.0, 2.0]


def test_market_prediction_supports_json_instance_payloads(monkeypatch):
    app = FastAPI()
    app.include_router(router, prefix="/api")
    client = TestClient(app)

    fake_runtime = FakeRuntimeClient('{"predictions":[{"score": 42.5}]}')
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_ENDPOINT_NAME", "car-price-endpoint")
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_CONTENT_TYPE", "application/json")
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_ACCEPT", "application/json")
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_REQUEST_FORMAT", "json_instances")
    monkeypatch.setattr(settings, "CAR_PRICE_MODEL_REFERENCE_YEAR", 2026)
    monkeypatch.setattr(settings, "CAR_PRICE_MODEL_OUTPUT_MULTIPLIER_VND", 28_100_000)
    monkeypatch.setattr(market_prediction, "_runtime_client", fake_runtime)

    res = client.post(
        "/api/market/prediction",
        json={
            "Present_Price": 8.1,
            "Kms_Driven": 10000,
            "Fuel_Type": "Petrol",
            "Seller_Type": "Dealer",
            "Transmission": "Manual",
            "Owner": 0,
            "Year": 2025,
        },
    )

    assert res.status_code == 200
    data = res.json()
    assert data["data"]["raw_model_prediction"] == 42.5

    call = fake_runtime.calls[0]
    assert call["ContentType"] == "application/json"
    assert call["Accept"] == "application/json"
    body = json.loads(call["Body"])
    assert body["instances"][0][0] == from_usd_input(8.1)
    assert body["instances"][0][1:] == [10000, 0, 0, 0, 0, 1]


def test_market_prediction_omits_accept_header_when_blank(monkeypatch):
    app = FastAPI()
    app.include_router(router, prefix="/api")
    client = TestClient(app)

    fake_runtime = FakeRuntimeClient("77.7")
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_ENDPOINT_NAME", "car-price-endpoint")
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_CONTENT_TYPE", "text/csv")
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_ACCEPT", "")
    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_REQUEST_FORMAT", "csv")
    monkeypatch.setattr(settings, "CAR_PRICE_MODEL_REFERENCE_YEAR", 2026)
    monkeypatch.setattr(settings, "CAR_PRICE_MODEL_OUTPUT_MULTIPLIER_VND", 28_100_000)
    monkeypatch.setattr(market_prediction, "_runtime_client", fake_runtime)

    res = client.post(
        "/api/market/prediction",
        json={
            "Present_Price": 6.2,
            "Kms_Driven": 21000,
            "Fuel_Type": "Diesel",
            "Seller_Type": "Individual",
            "Transmission": "Automatic",
            "Owner": 1,
            "Year": 2023,
        },
    )

    assert res.status_code == 200
    call = fake_runtime.calls[0]
    assert "Accept" not in call
    assert call["Body"] == f"{from_usd_input(6.2):g},21000,1,1,1,1,3"


def test_market_prediction_rejects_unknown_category(monkeypatch):
    app = FastAPI()
    app.include_router(router, prefix="/api")
    client = TestClient(app)

    monkeypatch.setattr(settings, "SAGEMAKER_CAR_PRICE_ENDPOINT_NAME", "car-price-endpoint")

    res = client.post(
        "/api/market/prediction",
        json={
            "Present_Price": 5.5,
            "Kms_Driven": 45000,
            "Fuel_Type": "Hybrid",
            "Seller_Type": "Individual",
            "Transmission": "Automatic",
            "Owner": 0,
            "Year": 2020,
        },
    )

    assert res.status_code == 400
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_CATEGORY"
