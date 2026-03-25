"""
router_market.py - Market prediction endpoint

GET  /api/market/prediction
POST /api/market/prediction
"""

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from intelligence.market_prediction import (
    InvalidPredictionInputError,
    PredictionError,
    PredictorMisconfiguredError,
    UnsupportedCategoryError,
    predict_car_price,
)
from models.schemas import CarPricePredictionRequest

router = APIRouter()


def _error(message: str, error_code: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "error_code": error_code},
    )


def _build_response(body: CarPricePredictionRequest):
    try:
        result = predict_car_price(body)
    except UnsupportedCategoryError as exc:
        return _error(str(exc), "INVALID_CATEGORY")
    except InvalidPredictionInputError as exc:
        return _error(str(exc), "INVALID_MODEL_INPUT")
    except PredictorMisconfiguredError as exc:
        return _error(str(exc), "SAGEMAKER_NOT_CONFIGURED", 503)
    except PredictionError as exc:
        return _error(str(exc), "SAGEMAKER_PREDICTION_FAILED", 502)

    return {
        "success": True,
        "data": {
            "predicted_price": result.predicted_price,
            "raw_model_prediction": result.raw_prediction,
            "model_input": {
                "present_price": body.Present_Price,
                "kms_driven": body.Kms_Driven,
                "fuel_type": body.Fuel_Type,
                "seller_type": body.Seller_Type,
                "transmission": body.Transmission,
                "owner": body.Owner,
                "year": body.Year,
                "car_age": result.car_age,
            },
            "prediction_unit": "VND",
            "feature_vector": result.feature_vector,
        },
    }


@router.post("/market/prediction")
def post_market_prediction(body: CarPricePredictionRequest):
    return _build_response(body)


@router.get("/market/prediction")
def get_market_prediction(
    Present_Price: float = Query(..., ge=0),
    Kms_Driven: float = Query(..., ge=0),
    Fuel_Type: str = Query(...),
    Seller_Type: str = Query(...),
    Transmission: str = Query(...),
    Owner: int = Query(..., ge=0),
    Year: int = Query(..., ge=1900),
):
    body = CarPricePredictionRequest(
        Present_Price=Present_Price,
        Kms_Driven=Kms_Driven,
        Fuel_Type=Fuel_Type,
        Seller_Type=Seller_Type,
        Transmission=Transmission,
        Owner=Owner,
        Year=Year,
    )
    return _build_response(body)
