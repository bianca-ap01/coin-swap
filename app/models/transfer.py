from pydantic import BaseModel, Field

class TransferRequest(BaseModel):
    receiver: str
    amount: float = Field(..., gt=0)
    currency: str = Field(..., pattern="^(USD|PEN)$")

class ConversionRequest(BaseModel):
    from_currency: str = Field(..., pattern="^(USD|PEN)$")
    to_currency: str = Field(..., pattern="^(USD|PEN)$")
    amount: float = Field(..., gt=0)

class DepositWithdrawRequest(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = Field(..., pattern="^(USD|PEN)$")
    operation: str = Field(..., pattern="^(deposit|withdraw)$")
