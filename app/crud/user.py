from sqlalchemy.orm import Session
from app.models.user import UserDB

def get_user_by_username(db: Session, username: str):
    return db.query(UserDB).filter(UserDB.username == username).first()

def create_user(db: Session, username: str):
    db_user = UserDB(username=username, balance_pen=100.0, balance_usd=0.0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user: UserDB):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
