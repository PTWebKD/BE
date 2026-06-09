import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register_success(client):
    resp = await client.post("/api/auth/register", json={
        "email": "newuser@test.com",
        "password": "secret123",
        "display_name": "New User",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["role"] == "member"


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    body = {"email": "dup@test.com", "password": "x", "display_name": "D"}
    await client.post("/api/auth/register", json=body)
    resp = await client.post("/api/auth/register", json=body)
    assert resp.status_code == 400
    assert resp.json()["detail"]["error"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_login_success(client, member_user):
    resp = await client.post("/api/auth/login", json={
        "email": "member@test.com",
        "password": "password123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client, member_user):
    resp = await client.post("/api/auth/login", json={
        "email": "member@test.com",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client, member_token):
    resp = await client.get("/api/users/me", headers={"Authorization": f"Bearer {member_token}"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["email"] == "member@test.com"
    assert data["role"] == "member"


@pytest.mark.asyncio
async def test_otp_flow(client):
    req = await client.post("/api/auth/guest/otp/request", json={"phone": "0901234567"})
    assert req.status_code == 200
    code = req.json()["data"]["dev_otp"]
    assert len(code) == 6

    verify = await client.post("/api/auth/guest/otp/verify", json={
        "phone": "0901234567",
        "otp_code": code,
    })
    assert verify.status_code == 200
    assert verify.json()["data"]["verified"] is True


@pytest.mark.asyncio
async def test_otp_wrong_code(client):
    await client.post("/api/auth/guest/otp/request", json={"phone": "0909999999"})
    resp = await client.post("/api/auth/guest/otp/verify", json={
        "phone": "0909999999",
        "otp_code": "000000",
    })
    assert resp.status_code == 401
