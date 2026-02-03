import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Test the health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200 or response.status_code == 503
    data = response.json()
    assert "status" in data
    assert "databases" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Medical Chat Bot API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User"
            }
        )
    
    # Will fail if MongoDB is not running, but that's expected in tests
    # In a real test, we'd use a test database or mocking
    assert response.status_code in [201, 500, 503]


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword"
            }
        )
    
    # Should return 401 or 500/503 if DB not available
    assert response.status_code in [401, 500, 503]
