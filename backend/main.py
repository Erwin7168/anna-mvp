import os
import requests
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Voor de demo-modus gebruiken we de bestaande engine
from outfit_engine import generate_outfits as generate_demo, EngineConfig

load_dotenv()

app = FastAPI(title="Anna MVP API", version="0.1.0")

# CORS (zodat je frontend op Netlify/localhost kan praten met deze backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Datamodellen ---------
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
    mode: Optional[str] = Field(None, description="'demo' of 'serpapi' (leeg = automatisch)")
    serpapi_api_key: Optional[str] = Field(None, description="optioneel: sleutel meesturen; leeg = servervariabele gebruiken")
    outfits_count: int = Field(3, description="aantal outfits (default 3)")

# --------- Meta endpoint ---------
@app.get("/api/meta")
def meta():
    key_env = os.getenv("SERPAPI_API_KEY", "")
    return {
        "has_serpapi": bool(key_env),
        "environment": "dev",
        "version": "0.1.0"
    }

# --------- Generate endpoint ---------
@app.post("/api/generate")
def generate(req: GenerateRequest):
    # 1) sleutel: neem uit body, of anders van de server (Render env var)
    env_key = os.getenv("SERPAPI_API_KEY") or ""
    key = (req.serpapi_api_key or "").strip() or env_key

    # 2) modus: automatisch op basis van sleutel, tenzij expliciet gezet
    auto_mode = "serpapi" if key else "demo"
    mode = (req.mode or auto_mode).lower()

    try:
        if mode == "serpapi" and key:
            return generate_with_serpapi(req.intake.dict(), key, req.outfits_count)
        else:
            # Demo-modus gebruikt de bestaande engine uit outfit_engine
            cfg = EngineConfig(mode="demo", serpapi_api_key=None, outfits_count=req.outfits_count)
            return generate_demo(intake=req.intake.dict(), config=cfg)
    except Exception:
        # Veiligheidsnet: val terug op demo in geval van fout
        cfg = EngineConfig(mode="demo", serpapi_api_key=None, outfits_count=req.outfits_count)
        return generate_demo(intake=req.intake.dict(), config=cfg)

# --------- SERPAPI implementatie (live zoeken) ---------
def _alloc(budget: float):
    alloc = {
        "outer": budget * 0.25,
        "top1": budget * 0.15,
        "top2": budget * 0.15,
        "bottom": budget * 0.20,
        "shoes": budget * 0.20,
        "tee": budget * 0.04,
        "accessory": budget * 0.01,
    }
    alloc["_total"] = round(sum(v for k, v in alloc.items() if k != "_total"), 2)
    return alloc

def _build_query(category: str, intake: dict) -> str:
    gender = {"male": "men", "female": "women"}.get((intake.get("gender") or "unisex").lower(), "unisex")
    styles = " ".join(intake.get("styles") or [])
    colors = " ".join(intake.get("favorite_colors") or [])
    terms = {
        "outer": "jacket blazer overshirt coat",
        "top1": "shirt knit sweater",
        "top2": "shirt knit sweater",
        "tee": "t-shirt tee",
        "bottom": "chino trousers jeans",
        "shoes": "sneakers shoes",
        "accessory": "belt scarf",
    }[category]
    return " ".join(x for x in [gender, styles, terms, colors] if x).strip()

def _serp_search(q: str, gl: str, api_key: str, num: int = 12):
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_shopping",
        "q": q,
        "gl": gl.lower(),   # landcode: nl, be, de, fr, uk, us
        "hl": "nl",
        "num": num,
        "api_key": api_key,
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json().get("shopping_results", []) or []

def _price_of(x):
    p = x.get("extracted_price") or x.get("price") or 0
    try:
        return float(p)
    except Exception:
        return 0.0

def _pick_item(results: list, max_price: float):
    # kies item met prijs zo dicht mogelijk bij budget (met 10% marge)
    candidates = [r for r in results if _price_of(r) > 0]
    within = [r for r in candidates if _price_of(r) <= max_price * 1.10]
    pool = within or candidates
    if not pool:
        return None
    pool.sort(key=lambda r: abs(_price_of(r) - max_price))
    return pool[0]

def _map_item(cat: str, r: dict):
    return {
        "category": cat,
        "title": r.get("title", "—"),
        "price": round(_price_of(r), 2),
        "currency": r.get("currency") or "EUR",
        "link": r.get("link") or "#",
        "image": r.get("thumbnail"),
        "merchant": r.get("source") or r.get("seller") or "",
        "cheaper_alternative": None,
    }

def generate_with_serpapi(intake: dict, api_key: str, outfits_count: int = 3):
    budget = float(intake.get("budget_total") or 250)
    alloc = _alloc(budget)
    gl = (intake.get("country") or "NL")[:2].lower()
    palette = {"colors": (intake.get("favorite_colors") or ["navy", "white", "grey", "black", "stone"])}

    categories = ["outer", "top1", "top2", "bottom", "shoes", "tee", "accessory"]
    cache = {}
    outfits = []

    for n in range(outfits_count or 3):
        items = []
        total = 0.0
        for cat in categories:
            q = _build_query(cat, intake)
            if q not in cache:
                cache[q] = _serp_search(q, gl, api_key, num=12)
            found = _pick_item(cache[q], alloc[cat])
            if found:
                item = _map_item(cat, found)
            else:
                item = {
                    "category": cat,
                    "title": "(geen resultaat gevonden — alternatief)",
                    "price": round(alloc[cat], 2),
                    "currency": "EUR",
                    "link": "#",
                    "image": None,
                    "merchant": "—",
                    "cheaper_alternative": None,
                }
            items.append(item)
            total += float(item.get("price") or 0)
        outfits.append({
            "name": f"Outfit {n+1}",
            "items": items,
            "total": round(total, 2),
            "currency": items[0].get("currency", "EUR"),
        })

    return {
        "palette": palette,
        "allocation": alloc,
        "outfits": outfits,
        "explanation": "Producten gezocht via Google Shopping (SerpAPI) op jouw stijl, land en budget. Bij lege resultaten kies ik een veilig alternatief.",
        "independent_note": "Anna is onafhankelijk: geen affiliate; links zijn puur gemak.",
        "country": intake.get("country") or "NL",
        "currency": outfits[0].get("currency", "EUR"),
    }

# --------- lokaal starten ---------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=True)
