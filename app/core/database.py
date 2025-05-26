from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import motor.motor_asyncio
from app.core.config import DATABASE_URL, MONGODB_URI, MONGODB_DB_NAME

# PostgreSQL engine y sesión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

# Cliente MongoDB asíncrono
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
mongo_db = mongo_client[MONGODB_DB_NAME]
transactions_collection = mongo_db["transactions"]
