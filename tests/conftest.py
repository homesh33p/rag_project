import pytest
from httpx import AsyncClient
from fastapi import FastAPI
import asyncio
from typing import AsyncGenerator, Generator

from app.main import app

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Yield an async client that can be used for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
