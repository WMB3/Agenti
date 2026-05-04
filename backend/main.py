import os
import asyncio
import logging
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from ingestion.scrapers.playwright_scraper import PlaywrightScraper
from ingestion.models import AuctionItem

class CarData(BaseModel):
    make: str
    model: str
    year: int
    mileage: int

class CarEvaluation(BaseModel):
    estimated_value: float
    condition: str
    recommendation: str

gemini_client = None
if os.getenv("GEMINI_API_KEY"):
    gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- CONFIGURATION ---
app = FastAPI(title="NEXUS Omni Terminal API")

allowed_origins_str = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SCRAPER SERVICE ---
scraper = PlaywrightScraper()

# --- ENDPOINTS ---
@app.get("/")
async def health_check():
    return {"status": "online", "system": "NEXUS Omni"}

@app.post("/api/v1/intercept", response_model=List[AuctionItem])
async def handle_intercept(payload: Dict = Body(...)):
    """
    Core interception endpoint for real-time scraping and forensics.
    """
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    try:
        items = await scraper.fetch_from_url(url)
        return items
    except Exception as e:
        logging.error(f"Intercept failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ghost-Intercept failed: {str(e)}")

@app.post("/api/v1/batch_intercept", response_model=List[List[AuctionItem]])
async def handle_batch_intercept(payloads: List[Dict] = Body(...)):
    """
    Batch interception for multiple targets simultaneously.
    """
    tasks = []
    for p in payloads:
        url = p.get("url")
        if url:
            tasks.append(scraper.fetch_from_url(url))

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        final_results = []
        for r in results:
            if isinstance(r, Exception):
                logging.error(f"Batch task failed: {r}")
                final_results.append([])
            else:
                final_results.append(r)
        return final_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze", response_model=CarEvaluation)
async def analyze_vehicle(car: CarData):
    """Sends vehicle data to Gemini and returns evaluation."""
    if not gemini_client:
        raise HTTPException(status_code=500, detail="Gemini client not configured.")

    prompt = f"Evaluate car: {car.year} {car.make} {car.model} with {car.mileage} miles. Provide estimated_value, condition, and recommendation as JSON."
    try:
        response = await gemini_client.aio.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        data = json.loads(response.text)
        return CarEvaluation(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze vehicle: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
