import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from outfit_engine import generate_outfits, EngineConfig

load_dotenv()

app = FastAPI(title="Anna MVP API", version="0.1.0")

# CORS for local development and simple hosting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Intake(BaseModel):
    purpose: str = Field(..., description="werk, vrije tijd, event, dagelijks, etc.")
    styles: List[str] = Field(..., description="max 2 stijlen: minimalistisch, casual, klassiek, sportief, creatief")
    gender: str = Field(..., description="male/female/unisex/non-binary")
    fit: Optional[str] = Field(None, description="recht, getailleerd, relaxed")
    age_range: Optional[str] = Field(None, description="18–25, 26–35, 36–45, 46–55, 56+")
    country: str = Field(..., description="NL, BE, DE, FR, UK, US, etc.")
    currency: Optional[str] = Field(None, description="EUR, GBP, USD (optioneel, afgeleid van land)")
    budget_total: Optional[float] = Field(None, description="Totaalbudget (bijv. 250)")
    budget_per_item: Optional[float] = Field(None, description="Budget per item als alternatief")
    sizes: Optional[Dict[str, str]] = Field(None, description="maat per categorie, optioneel")
    favorite_colors: Optional[List[str]] = Field(None, description="voorkeurskleuren")
    materials_avoid: Optional[List[str]] = Field(None, description="materialen/allergieën")
    accessibility: Optional[Dict[str, Any]] = Field(None, description="toegankelijkheidswensen")
    sustainability_preference: Optional[bool] = Field(False, description="zacht criterium: bij voorkeur duurzaam")

class GenerateRequest(BaseModel):
    intake: Intake
    mode: str = Field("demo", description="'demo' of 'serpapi'")
    serpapi_api_key: Optional[str] = Field(None, description="optie: override van .env")
    outfits_count: int = Field(3, description="aantal outfits (default 3)")

@app.get("/api/meta")
def meta():
    key_env = os.getenv("SERPAPI_API_KEY", "")
    return {
        "has_serpapi": bool(key_env),
        "environment": "dev",
        "version": "0.1.0"
    }

@app.post("/api/generate")
def api_generate(req: GenerateRequest):
    # Read config
    serp_key = req.serpapi_api_key or os.getenv("SERPAPI_API_KEY", None)
    config = EngineConfig(
        mode=req.mode,
        serpapi_api_key=serp_key,
        outfits_count=req.outfits_count
    )
    try:
        result = generate_outfits(intake=req.intake.dict(), config=config)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)