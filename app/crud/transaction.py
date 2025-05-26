from app.core.database import transactions_collection
from app.models.transaction import TransactionOut
from typing import List
import datetime

async def insert_transaction(description: str, username: str):
    await transactions_collection.insert_one({
        "timestamp": datetime.datetime.utcnow(),
        "description": description,
        "username": username,
    })

async def get_transactions_by_user(username: str) -> List[TransactionOut]:
    cursor = transactions_collection.find({"username": username}).sort("timestamp", -1)
    results = []
    async for doc in cursor:
        results.append(TransactionOut(
            timestamp=doc["timestamp"],
            description=doc["description"],
            username=doc["username"]
        ))
    return results
