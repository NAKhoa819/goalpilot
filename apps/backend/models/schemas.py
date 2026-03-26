from typing import List, Literal

from pydantic import BaseModel, Field

class StrategyResponse(BaseModel):
    strategy: Literal["A", "B", "None"] = Field(
        ...,
        description="The selected strategy. 'A' for Cost Optimization, 'B' for Goal Re-alignment."
    )
    reasoning: str = Field(
        ..., 
        description="A concise explanation of why this strategy was chosen based on the Sustainability Index and context."
    )
    remediation_steps: List[str] = Field(
        ..., 
        description="A list of specific, actionable steps the user can take to execute the strategy."
    )


class AtRiskProposalResponse(BaseModel):
    risk_summary: str = Field(
        ...,
        description="A concise explanation of why the current goal is off track."
    )
    plan_a_reason: str = Field(
        ...,
        description="A concise explanation of why the increase-savings option is valid."
    )
    plan_a_saving_tips: List[str] = Field(
        default_factory=list,
        description="Concrete savings ideas the user can try to support Plan A."
    )
    plan_b_reason: str = Field(
        ...,
        description="A concise explanation of why the deadline-extension option is valid."
    )


class CarGoalIntentResponse(BaseModel):
    is_car_purchase_goal: bool = Field(
        default=False,
        description="True when the user message is asking to create or add a goal for buying a car."
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Model confidence for the car-goal classification."
    )


class CarPricePredictionRequest(BaseModel):
    Present_Price: float = Field(..., ge=0)
    Kms_Driven: float = Field(..., ge=0)
    Fuel_Type: str
    Seller_Type: str
    Transmission: str
    Owner: int = Field(..., ge=0)
    Year: int = Field(..., ge=1900)
