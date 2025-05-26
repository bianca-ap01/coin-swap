from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.crud.transaction import get_transactions_by_user
from sqlalchemy.orm import Session
from app.api.deps import get_db

router = APIRouter()

@router.get("/", response_model=list)
async def get_transactions(current_user = Depends(get_current_user)):
    return await get_transactions_by_user(current_user.username)
