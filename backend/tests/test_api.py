import pytest

def test_ping(client):
    """Test the health check endpoint."""
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "running" in response.json().get("message", "").lower()

def test_cors_headers(client):
    """Test that CORS headers are correctly applied."""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-Requested-With"
    }
    response = client.options("/faq", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
