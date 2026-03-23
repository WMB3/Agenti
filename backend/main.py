import os
from asyncio import gather
import logging
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from ingestion.scrapers.playwright_scraper import PlaywrightScraper
from ingestion.models import AuctionItem

# --- CONFIGURATION ---
app = FastAPI(title="NEXUS Omni Terminal API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        results = await gather(*tasks, return_exceptions=True)
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
