from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.post("/transfer/user/balance/change/")
async def deposit():
    await asyncio.sleep(0.5)
    return {"status": "ok", "message": "Deposit simulated"}

@app.post("/transfer/transfer/")
async def transfer():
    await asyncio.sleep(0.5)
    return {"status": "ok", "message": "Transfer simulated"}

@app.post("/transfer/convert/")
async def convert():
    await asyncio.sleep(0.5)
    return {"status": "ok", "message": "Conversion simulated"} 