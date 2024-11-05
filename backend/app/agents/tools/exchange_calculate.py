import json
import os
from typing import Optional
import requests
from datetime import datetime

from app.agents.tools.agent_tool import AgentTool
from app.repositories.models.custom_bot import BotModel
from app.routes.schemas.conversation import type_model_name
from pydantic import BaseModel, Field, root_validator


class CurrencyConvertInput(BaseModel):
    amount: float = Field(description="The amount of money to convert.")
    base_currency: str = Field(
        description="The source currency code (e.g., USD, TWD, EUR, JPY)."
    )
    target_currency: str = Field(
        description="The target currency code (e.g., USD, TWD, EUR, JPY)."
    )

    @root_validator(pre=True)
    def validate_currencies(cls, values):
        supported_currencies = ["USD","TWD", "EUR", "JPY", "GBP", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD"]
        base_curr = values.get("base_currency", "").upper()
        target_curr = values.get("target_currency", "").upper()
        
        if base_curr not in supported_currencies:
            raise ValueError(
                f"From currency must be one of: {', '.join(supported_currencies)}"
            )
        if target_curr not in supported_currencies:
            raise ValueError(
                f"To currency must be one of: {', '.join(supported_currencies)}"
            )
        
        values["base_currency"] = base_curr
        values["target_currency"] = target_curr
        return values


def currency_convert(
    tool_input: CurrencyConvertInput, bot: BotModel | None, model: type_model_name | None
) -> str:
    """
    Convert currency using Exchange Rate API
    """
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        error_result = {
            "success": False,
            "error": "EXCHANGE_RATE_API_KEY environment variable is not set",
            "from": None,
            "to": None,
            "rate": None,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_result)
        
    base_url = "https://v6.exchangerate-api.com/v6"
    
    try:
        url = f"{base_url}/{api_key}/pair/{tool_input.base_currency}/{tool_input.target_currency}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("result") == "success":
            rate = data.get("conversion_rate")
            exchange_rate_time = data.get("time_last_update_utc")
            converted_amount = tool_input.amount * rate
            
            result = {
                "success": True,
                "error": None,
                "from": {
                    "currency": tool_input.base_currency,
                    "amount": tool_input.amount
                },
                "to": {
                    "currency": tool_input.target_currency,
                    "amount": round(converted_amount, 2)
                },
                "rate": rate,
                "timestamp": exchange_rate_time
            }
        else:
            result = {
                "success": False,
                "error": "Failed to get exchange rate",
                "from": None,
                "to": None,
                "rate": None,
                "timestamp": datetime.now().isoformat()
            }
            
        return json.dumps(result)
        
    except requests.exceptions.RequestException as e:
        error_result = {
            "success": False,
            "error": f"API request failed: {str(e)}",
            "from": None,
            "to": None,
            "rate": None,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_result)


currency_convert_tool = AgentTool(
    name="currency_convert",
    description="Convert amount from one currency to another using real-time exchange rates.",
    args_schema=CurrencyConvertInput,
    function=currency_convert,
)