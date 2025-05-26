from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.currency_client import currency_api_client

router = APIRouter()

class AdapterSelection(BaseModel):
    key: str

@router.get("/rates/")
async def list_rates(from_currency: str = "USD", to_currency: str = "PEN"):
    rates = await currency_api_client.list_all_rates(from_currency, to_currency)
    return rates

@router.post("/select/")
def select_adapter(selection: AdapterSelection):
    try:
        currency_api_client.select_adapter(selection.key)
        return {"message": f"Adaptador cambiado a {currency_api_client.get_current_adapter_name()}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
