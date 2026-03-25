import uuid
import asyncio
from decimal import Decimal
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_wallet_implicitly(client: AsyncClient):
    wallet_uuid = uuid.uuid4()

    
    response = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert response.status_code == 404

    
    response = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "100.50"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(wallet_uuid)
    assert Decimal(data["balance"]) == Decimal("100.50")

    # Проверка баланса
    response = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("100.50")

@pytest.mark.asyncio
async def test_deposit_and_withdraw(client: AsyncClient):
    wallet_uuid = uuid.uuid4()

    # Пополнение
    await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "200"}
    )
    response = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert Decimal(response.json()["balance"]) == Decimal("200")

    # Снятие
    response = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": "50"}
    )
    assert response.status_code == 200
    assert Decimal(response.json()["balance"]) == Decimal("150")

    # Недостаточно средств
    response = await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "WITHDRAW", "amount": "200"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient funds"

@pytest.mark.asyncio
async def test_concurrent_updates(client: AsyncClient):
    wallet_uuid = uuid.uuid4()

    # Создаём кошелёк
    await client.post(
        f"/api/v1/wallets/{wallet_uuid}/operation",
        json={"operation_type": "DEPOSIT", "amount": "100"}
    )

    async def do_withdraw(amount):
        return await client.post(
            f"/api/v1/wallets/{wallet_uuid}/operation",
            json={"operation_type": "WITHDRAW", "amount": amount}
        )

    tasks = [do_withdraw("20") for _ in range(5)]
    results = await asyncio.gather(*tasks)
    for res in results:
        assert res.status_code == 200

    final = await client.get(f"/api/v1/wallets/{wallet_uuid}")
    assert Decimal(final.json()["balance"]) == Decimal("0")