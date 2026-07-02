import asyncio
import time
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import BaseModel

class DummyCarEvaluation(BaseModel):
    analysis: str = "good"
    estimated_value: float = 25000.0
    recommendation: str = "buy"

async def main():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        payload = {"make": "Toyota", "model": "Camry", "year": 2020}

        # Test concurrent requests
        start_time = time.time()
        tasks = []
        for _ in range(5):
            tasks.append(ac.post("/api/analyze", json=payload))

        results = await asyncio.gather(*tasks)
        end_time = time.time()

        print(f"Total time for 5 requests: {end_time - start_time:.2f} seconds")
        for r in results:
            print(r.status_code)

if __name__ == "__main__":
    asyncio.run(main())
