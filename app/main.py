from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, users, transfer, transactions, currency
from app.core.database import Base, engine, SessionLocal
from app.models.user import UserDB
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambiar en producción por dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Inicializar usuarios con saldo
def init_users(db: Session):
    # Verificar si los usuarios ya existen
    user_x = db.query(UserDB).filter(UserDB.username == "X").first()
    user_y = db.query(UserDB).filter(UserDB.username == "Y").first()

    if not user_x:
        user_x = UserDB(username="X", balance_pen=100, balance_usd=200)
        db.add(user_x)

    if not user_y:
        user_y = UserDB(username="Y", balance_pen=50, balance_usd=100)
        db.add(user_y)

    db.commit()

# Inicializar la base de datos con los usuarios X y Y
def init_db():
    db = SessionLocal()
    try:
        init_users(db)
    finally:
        db.close()

init_db()

# Incluir routers de las rutas
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(transfer.router, prefix="/transfer", tags=["transfer"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(currency.router, prefix="/currency", tags=["currency"])

