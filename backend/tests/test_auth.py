import pytest

@pytest.mark.asyncio
async def test_login_refresh_me_logout(client):
    response = await client.post("/api/v1/auth/login", json={"organization_slug":"acme","email":"rep@acme.com","password":"CorrectHorse1"})
    assert response.status_code == 200
    tokens = response.json()
    assert tokens["access_token"] and tokens["refresh_token"]
    me = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "rep@acme.com"
    assert me.json()["full_name"] == "Rep User"
    assert "users:read" in me.json()["permissions"]
    refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200
    assert refreshed.json()["refresh_token"] != tokens["refresh_token"]
    replay = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert replay.status_code == 401
    logout = await client.post("/api/v1/auth/logout", json={"refresh_token": refreshed.json()["refresh_token"]})
    assert logout.status_code == 204
    rejected = await client.post("/api/v1/auth/refresh", json={"refresh_token": refreshed.json()["refresh_token"]})
    assert rejected.status_code == 401

@pytest.mark.asyncio
async def test_login_rejects_bad_password(client):
    response = await client.post("/api/v1/auth/login", json={"organization_slug":"acme","email":"rep@acme.com","password":"WrongHorse1"})
    assert response.status_code == 401
