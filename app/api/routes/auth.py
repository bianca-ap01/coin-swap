from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.crud.user import get_user_by_username, create_user
from app.core.security import create_access_token
from app.api.deps import get_db
from app.models.user import UserCreate

router = APIRouter()

@router.post("/register/", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, user.username):
        raise HTTPException(400, "Usuario ya existe")
    create_user(db, user.username)
    return {"msg": "Usuario creado con éxito"}

@router.post("/token/")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user:
        raise HTTPException(400, "Usuario no encontrado")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
