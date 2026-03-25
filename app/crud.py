from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError
from app.models import Wallet, Transaction
from app.schemas import OperationType

async def get_wallet(db: AsyncSession, wallet_uuid: str) -> Wallet:
    stmt = select(Wallet).where(Wallet.id == wallet_uuid)
    result = await db.execute(stmt)
    wallet = result.scalar_one_or_none()
    if wallet is None:
        raise NoResultFound
    return wallet

async def get_transactions(db: AsyncSession, wallet_uuid: str, limit: int = 10):
    stmt = select(Transaction).where(Transaction.wallet_id == wallet_uuid).order_by(Transaction.timestamp.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_balance(
    db: AsyncSession,
    wallet_uuid: str,
    operation_type: OperationType,
    amount: Decimal
) -> Decimal:
    while True:
        stmt = select(Wallet).where(Wallet.id == wallet_uuid).with_for_update()
        result = await db.execute(stmt)
        wallet = result.scalar_one_or_none()

        if wallet is None:
            if operation_type == OperationType.WITHDRAW:
                raise NoResultFound
            wallet = Wallet(id=wallet_uuid, balance=Decimal("0.00"))
            db.add(wallet)
            try:
                await db.flush()
                break
            except IntegrityError:
                await db.rollback()
                continue
        else:
            break

    if operation_type == OperationType.DEPOSIT:
        wallet.balance += amount
    else:
        if wallet.balance < amount:
            raise ValueError("Insufficient funds")
        wallet.balance -= amount

    db.add(wallet)

    
    transaction = Transaction(
        wallet_id=wallet.id,
        operation_type=operation_type.value,
        amount=amount,
        timestamp=datetime.utcnow()
    )
    db.add(transaction)
    await db.flush()

    return wallet.balance