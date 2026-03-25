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


class CarPricePredictionRequest(BaseModel):
    Present_Price: float = Field(..., ge=0)
    Kms_Driven: float = Field(..., ge=0)
    Fuel_Type: str
    Seller_Type: str
    Transmission: str
    Owner: int = Field(..., ge=0)
    Year: int = Field(..., ge=1900)
