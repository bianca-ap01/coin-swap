from pydantic import BaseModel
from datetime import datetime

class TransactionOut(BaseModel):
    timestamp: datetime
    description: str
    username: str
