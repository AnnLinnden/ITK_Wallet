import pytest
import asyncio
import os

os.environ['TESTING'] = 'True'


@pytest.mark.asyncio
async def test_get_wallet_success(client, fill_test_table):
    test_wallet = fill_test_table["zero balance"]
    response = await client.get(f"/api/v1/wallets/{test_wallet.uuid}")
    assert response.status_code == 200
    answer_json = response.json()
    assert answer_json["uuid"] == test_wallet.uuid
    assert answer_json["balance"] == test_wallet.balance


@pytest.mark.asyncio
async def test_get_wallet_not_found(client):
    response = await client.get("/api/v1/wallets/00000000-0000-0000-0000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_deposit_success(client, fill_test_table):
    test_wallet = fill_test_table["zero balance"]
    response = await client.post(f"/api/v1/wallets/{test_wallet.uuid}/deposit", json={"amount": 100})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_deposit_negative_amount(client, fill_test_table):
    test_wallet = fill_test_table["zero balance"]
    response = await client.post(f"/api/v1/wallets/{test_wallet.uuid}/deposit", json={"amount": -100})
    assert response.status_code == 422  # Unprocessable Entity от Pydantic


@pytest.mark.asyncio
async def test_deposit_new_wallet(client):
    response = await client.post("/api/v1/wallets/00000000-0000-0000-0000/deposit", json={"amount": 100})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_withdraw_success(client, fill_test_table):
    test_wallet = fill_test_table["500 balance"]
    response = await client.post(f"/api/v1/wallets/{test_wallet.uuid}/withdraw", json={"amount": 500})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_withdraw_new_wallet(client):
    response = await client.post("/api/v1/wallets/00000000-0000-0000-0000/withdraw", json={"amount": 50})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_withdraw_negative_amount(client, fill_test_table):
    test_wallet = fill_test_table["100 balance"]
    response = await client.post(f"/api/v1/wallets/{test_wallet.uuid}/withdraw", json={"amount": -50})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_withdraw_not_enough_money(client, fill_test_table):
    test_wallet = fill_test_table["100 balance"]
    response = await client.post(f"/api/v1/wallets/{test_wallet.uuid}/withdraw", json={"amount": 150})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_concurrent_requests_success(client, fill_test_table, test_db_session):
    test_wallet = fill_test_table["zero balance"]

    async def make_deposit():
        return await client.post(f"/api/v1/wallets/{test_wallet.uuid}/deposit", json={"amount": 150})

    async def make_withdraw():
        return await client.post(f"/api/v1/wallets/{test_wallet.uuid}/withdraw", json={"amount": 200})

    responses = [await make_deposit(), await make_deposit(), await make_withdraw()]
    await test_db_session.refresh(test_wallet)  # без этого у нас на балансе отобразится 0, а не 100
    for response in responses:
        assert response.status_code == 200
        assert test_wallet.balance == 100


@pytest.mark.asyncio
async def test_concurrent_requests_fail(client, fill_test_table, test_db_session):
    test_wallet = fill_test_table["zero balance"]

    async def make_deposit():
        return await client.post(f"/api/v1/wallets/{test_wallet.uuid}/deposit", json={"amount": 150})

    async def make_withdraw():
        return await client.post(f"/api/v1/wallets/{test_wallet.uuid}/withdraw", json={"amount": 200})

    responses = [await make_deposit(), await make_withdraw(), await make_withdraw()]
    await test_db_session.refresh(test_wallet)
    assert responses[0].status_code == 200
    assert responses[1].status_code == 400
    assert responses[2].status_code == 400
