from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.api.deps import get_db
from app.models.user import User, UserDB

router = APIRouter()

@router.get("/me/balance/", response_model=User)
def read_own_balance(current_user: UserDB = Depends(get_current_user)):
    return User(
        username=current_user.username,
        balance_pen=current_user.balance_pen,
        balance_usd=current_user.balance_usd,
    )
