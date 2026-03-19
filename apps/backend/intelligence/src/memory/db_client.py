import boto3
from typing import Dict, Any

def get_user_financial_profile(user_id: str) -> Dict[str, Any]:
    """
    Fetches the user's financial profile from Amazon DynamoDB to drive the intelligence math.
    
    Keys retrieved:
    - mu_hist (float): Historical mean spending.
    - sigma_hist (float): Historical standard deviation.
    - beta_prop (float): Proposed budget/beta for the current period.
    - last_update_timestamp (float): The 't' value for freshness (Unix timestamp).
    - data_completeness (float): The R_comp score (0.0 to 1.0).
    - market_volatility (float): The V_mkt value.
    """
    try:
        # Initialize boto3 DynamoDB resource
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.Table("UserProfileData")
        
        response = table.get_item(Key={'user_id': user_id})
        item = response.get('Item', {})
        
        # Return strict mapping expected by core.intelligence
        return {
            "mu_hist": float(item.get("mu_hist", 0.0)),
            "sigma_hist": float(item.get("sigma_hist", 0.0)),
            "beta_prop": float(item.get("beta_prop", 0.0)),
            "last_update_timestamp": float(item.get("last_update_timestamp", 0.0)),
            "data_completeness": float(item.get("data_completeness", 1.0)),
            "market_volatility": float(item.get("market_volatility", 0.0))
        }
    except Exception as e:
        print(f"DynamoDB Fetch Error for user {user_id}: {e}")
        return {}
