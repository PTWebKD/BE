import pytest


@pytest.mark.asyncio
async def test_list_gear_public(client):
    resp = await client.get("/api/gear/")
    assert resp.status_code == 200
    assert isinstance(resp.json()["data"], list)


@pytest.mark.asyncio
async def test_gear_not_found(client):
    resp = await client.get("/api/gear/GEAR-XXXX-XXXX")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_member_can_list_for_rent(client, member_token):
    resp = await client.post("/api/gear/", json={
        "name": "Test Dumbbell",
        "category": "Weights",
        "condition_rating": 3,
        "listing_type": "rent",
        "rent_price_day": 50000,
    }, headers={"Authorization": f"Bearer {member_token}"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["listing_type"] == "rent"
    assert data["lister_role"] == "member"
    assert data["gear_id"].startswith("GEAR-")


@pytest.mark.asyncio
async def test_member_cannot_sell(client, member_token):
    resp = await client.post("/api/gear/", json={
        "name": "Barbell",
        "category": "Weights",
        "condition_rating": 4,
        "listing_type": "sell",
        "sell_price": 500000,
    }, headers={"Authorization": f"Bearer {member_token}"})
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "MEMBER_CANNOT_SELL"


@pytest.mark.asyncio
async def test_gym_owner_can_sell(client, owner_token):
    resp = await client.post("/api/gear/", json={
        "name": "Olympic Barbell",
        "category": "Weights",
        "condition_rating": 5,
        "listing_type": "sell",
        "sell_price": 3000000,
    }, headers={"Authorization": f"Bearer {owner_token}"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["listing_type"] == "sell"
    assert data["lister_role"] == "gym_owner"


@pytest.mark.asyncio
async def test_lifecycle_is_created_on_listing(client, member_token):
    create_resp = await client.post("/api/gear/", json={
        "name": "Yoga Mat",
        "category": "Accessories",
        "condition_rating": 4,
        "listing_type": "rent",
        "rent_price_day": 30000,
    }, headers={"Authorization": f"Bearer {member_token}"})
    gear_id = create_resp.json()["data"]["gear_id"]

    lifecycle_resp = await client.get(f"/api/gear/{gear_id}/lifecycle")
    assert lifecycle_resp.status_code == 200
    events = lifecycle_resp.json()["data"]
    assert len(events) >= 1
    assert events[0]["action"] == "listed"
