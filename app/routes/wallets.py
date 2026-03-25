from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/v1/wallets", tags=["wallets"])

@router.post("/{wallet_uuid}/operation", response_model=schemas.WalletResponse)
async def perform_operation(
    wallet_uuid: UUID,
    operation: schemas.OperationRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        async with db.begin():
            new_balance = await crud.update_balance(
                db, str(wallet_uuid), operation.operation_type, operation.amount
            )
            transactions = await crud.get_transactions(db, str(wallet_uuid), limit=10)
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return schemas.WalletResponse(id=wallet_uuid, balance=new_balance, transactions=transactions)

@router.get("/{wallet_uuid}", response_model=schemas.WalletResponse)
async def get_wallet_balance(
    wallet_uuid: UUID,
    db: AsyncSession = Depends(get_db),
    include_history: bool = Query(False, description="Include transaction history")
):
    try:
        wallet = await crud.get_wallet(db, str(wallet_uuid))
        if include_history:
            transactions = await crud.get_transactions(db, str(wallet_uuid), limit=10)
        else:
            transactions = []
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")
    return schemas.WalletResponse(id=wallet.id, balance=wallet.balance, transactions=transactions)