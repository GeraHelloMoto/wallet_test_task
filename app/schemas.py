from decimal import Decimal
from enum import Enum
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"

class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: Decimal = Field(gt=0, decimal_places=2)

    @field_validator("amount")
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

class TransactionResponse(BaseModel):
    id: int
    operation_type: str
    amount: Decimal
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class WalletResponse(BaseModel):
    id: UUID
    balance: Decimal
    transactions: list[TransactionResponse] = []

    model_config = ConfigDict(from_attributes=True)