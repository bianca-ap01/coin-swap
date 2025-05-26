from sqlalchemy import Column, Integer, String, Float
from app.core.database import Base
from pydantic import BaseModel

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    balance_pen = Column(Float, default=100.0)
    balance_usd = Column(Float, default=0.0)

class User(BaseModel):
    username: str
    balance_pen: float
    balance_usd: float

class UserCreate(BaseModel):
    username: str
