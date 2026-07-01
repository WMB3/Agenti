import asyncio
import time
from httpx import AsyncClient, ASGITransport
from main import app
from unittest.mock import patch, MagicMock, AsyncMock

# Add test endpoint implementation for bench
import main
from fastapi import HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types

class CarData(BaseModel):
    make: str
    model: str
    year: int

class CarEvaluation(BaseModel):
    analysis: str
    estimated_value: float
    recommendation: str

main.gemini_client = MagicMock()
main.gemini_client.models.generate_content = MagicMock()

# --- SYNCHRONOUS VERSION ---
@main.app.post("/api/analyze_sync", response_model=CarEvaluation)
async def analyze_vehicle_sync(car: CarData):
    if not main.gemini_client:
        raise HTTPException(status_code=500, detail="Gemini client not configured.")

    prompt = f"Analyze car: {car.make} {car.model} {car.year}"

    try:
        response = main.gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_schema=CarEvaluation, response_mime_type='application/json')
        )
        return response.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ASYNCHRONOUS VERSION ---
@main.app.post("/api/analyze_async", response_model=CarEvaluation)
async def analyze_vehicle_async(car: CarData):
    if not main.gemini_client:
        raise HTTPException(status_code=500, detail="Gemini client not configured.")

    prompt = f"Analyze car: {car.make} {car.model} {car.year}"

    try:
        response = await main.gemini_client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(response_schema=CarEvaluation, response_mime_type='application/json')
        )
        return response.parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_benchmark(endpoint, mock_sleep, is_async=False):
    payload = {"make": "Toyota", "model": "Camry", "year": 2020}

    mock_response = MagicMock()
    mock_response.parsed = CarEvaluation(analysis="good", estimated_value=25000.0, recommendation="buy")

    if is_async:
        async def mock_async_call(*args, **kwargs):
            await asyncio.sleep(mock_sleep)
            return mock_response
        main.gemini_client.aio = MagicMock()
        main.gemini_client.aio.models.generate_content = mock_async_call
    else:
        def mock_sync_call(*args, **kwargs):
            time.sleep(mock_sleep)
            return mock_response
        main.gemini_client.models.generate_content = mock_sync_call

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        start_time = time.time()
        # Make 10 concurrent requests
        tasks = [ac.post(endpoint, json=payload) for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        for r in responses:
            assert r.status_code == 200, f"Failed: {r.status_code} - {r.text}"

        return end_time - start_time

async def main_bench():
    print("Running benchmark...")
    sync_time = await run_benchmark("/api/analyze_sync", 0.1, is_async=False)
    print(f"Sync endpoint time (10 concurrent requests, 0.1s delay each): {sync_time:.2f}s")

    async_time = await run_benchmark("/api/analyze_async", 0.1, is_async=True)
    print(f"Async endpoint time (10 concurrent requests, 0.1s delay each): {async_time:.2f}s")

    print(f"Improvement: {sync_time / async_time:.2f}x faster")

if __name__ == "__main__":
    asyncio.run(main_bench())
