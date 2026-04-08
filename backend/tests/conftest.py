import pytest
from fastapi.testclient import TestClient
import httpx
from typing import AsyncGenerator
import sys
import os

# Add the backend directory to sys.path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

import pytest_asyncio

@pytest.fixture
def client():
    # We use TestClient from fastapi.testclient for synchronous endpoints
    with TestClient(app) as c:
        yield c

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    # For async endpoints, explicitly hitting the app router
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
