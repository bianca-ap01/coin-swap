from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.api.deps import get_db
from app.crud.user import get_user_by_username
from app.crud.transaction import insert_transaction
from app.core.currency_client import currency_api_client
from app.models.user import UserDB
from app.models.transfer import TransferRequest, ConversionRequest, DepositWithdrawRequest
import asyncio

router = APIRouter()

@router.post("/transfer/")
async def transfer(req: TransferRequest, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    receiver = get_user_by_username(db, req.receiver)
    if not receiver:
        raise HTTPException(404, "Usuario receptor no encontrado")

    if req.currency == "PEN":
        if current_user.balance_pen < req.amount:
            raise HTTPException(400, "Saldo insuficiente en PEN")
        current_user.balance_pen -= req.amount
        receiver.balance_pen += req.amount
    else:
        if current_user.balance_usd < req.amount:
            raise HTTPException(400, "Saldo insuficiente en USD")
        current_user.balance_usd -= req.amount
        receiver.balance_usd += req.amount

    db.commit()

    desc_sender = f"{current_user.username} transfirió {req.amount} {req.currency} a {receiver.username}"
    desc_receiver = f"{receiver.username} recibió {req.amount} {req.currency} de {current_user.username}"

    asyncio.create_task(insert_transaction(desc_sender, current_user.username))
    asyncio.create_task(insert_transaction(desc_receiver, receiver.username))

    return {"message": desc_sender}


@router.post("/convert/")
async def convert(req: ConversionRequest, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.from_currency == req.to_currency:
        raise HTTPException(400, "Las monedas origen y destino deben ser diferentes")

    if req.from_currency == "PEN" and current_user.balance_pen < req.amount:
        raise HTTPException(400, "Saldo insuficiente en PEN")
    if req.from_currency == "USD" and current_user.balance_usd < req.amount:
        raise HTTPException(400, "Saldo insuficiente en USD")

    tasa = await currency_api_client.get_rate(req.from_currency, req.to_currency)

    if req.from_currency == "PEN" and req.to_currency == "USD":
        converted = req.amount * tasa
        current_user.balance_pen -= req.amount
        current_user.balance_usd += converted
        desc = f"{current_user.username} convirtió {req.amount:.2f} PEN a {converted:.2f} USD (tasa {tasa:.4f})"
    else:
        converted = req.amount * tasa
        current_user.balance_usd -= req.amount
        current_user.balance_pen += converted
        desc = f"{current_user.username} convirtió {req.amount:.2f} USD a {converted:.2f} PEN (tasa {tasa:.4f})"

    db.commit()

    await insert_transaction(desc, current_user.username)

    return {"message": desc}

@router.post("/user/balance/change/")
async def change_balance(req: DepositWithdrawRequest, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    if req.operation == "deposit":
        if req.currency == "USD":
            current_user.balance_usd += req.amount
        else:
            current_user.balance_pen += req.amount
        desc = f"{current_user.username} depositó {req.amount} {req.currency}"
    else:
        if req.currency == "USD":
            if current_user.balance_usd < req.amount:
                raise HTTPException(400, "Saldo insuficiente en USD para retiro")
            current_user.balance_usd -= req.amount
        else:
            if current_user.balance_pen < req.amount:
                raise HTTPException(400, "Saldo insuficiente en PEN para retiro")
            current_user.balance_pen -= req.amount
        desc = f"{current_user.username} retiró {req.amount} {req.currency}"

    db.commit()

    asyncio.create_task(insert_transaction(desc, current_user.username))

    return {"message": desc}
