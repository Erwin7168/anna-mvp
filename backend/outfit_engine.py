import os
import json
import random
import math
import requests
from typing import Dict, Any, List, Optional, Tuple

from style_presets import STYLE_KEYWORDS, COUNTRY_SHOPS, DEFAULT_PALETTES, CURRENCY_BY_COUNTRY, DEMO_FALLBACK_ITEMS

class EngineConfig:
    def __init__(self, mode: str = "demo", serpapi_api_key: Optional[str] = None, outfits_count: int = 3):
        assert mode in ("demo", "serpapi"), "mode must be 'demo' or 'serpapi'"
        self.mode = mode
        self.serpapi_api_key = serpapi_api_key
        self.outfits_count = outfits_count

def _normalize_styles(styles: List[str]) -> List[str]:
    normalized = []
    for s in styles:
        key = s.strip().lower()
        if key in STYLE_KEYWORDS:
            normalized.append(key)
    if not normalized:
        normalized = ["casual"]
    return normalized[:2]

def _pick_palette(styles: List[str], favorites: Optional[List[str]]) -> Dict[str, Any]:
    # Simple merge: start from style palettes, then inject favorite hues if provided
    base = []
    for s in styles:
        base.extend(DEFAULT_PALETTES.get(s, []))
    # Deduplicate preserving order
    seen = set()
    base = [c for c in base if not (c in seen or seen.add(c))]
    if favorites:
        # Put favorites first if not already there
        favs = [f.lower() for f in favorites]
        base = [*favs, *[c for c in base if c not in favs]]
    # Guarantee at least 4 colors
    if len(base) < 4:
        base += ["navy", "white", "black", "grey"]
    return {"colors": base[:8]}

def _derive_currency(country: str, currency_override: Optional[str]) -> str:
    if currency_override:
        return currency_override
    return CURRENCY_BY_COUNTRY.get(country.upper(), "EUR")

def _allocate_budget(intake: Dict[str, Any]) -> Dict[str, float]:
    total = intake.get("budget_total")
    per_item = intake.get("budget_per_item")
    # 7 items target (can flex to 8)
    categories = ["outer", "top1", "top2", "bottom", "shoes", "tee", "accessory"]
    weights = {"outer": 0.25, "top1": 0.15, "top2": 0.15, "bottom": 0.2, "shoes": 0.2, "tee": 0.03, "accessory": 0.02}
    if per_item and not total:
        total = per_item * len(categories)
    if not total:
        total = 250.0  # sensible default
    allocation = {cat: max(10.0, round(total * weights[cat], 2)) for cat in categories}
    allocation["_total"] = total
    return allocation

def _build_queries(intake: Dict[str, Any], palette: Dict[str, Any]) -> Dict[str, List[str]]:
    country = intake["country"].upper()
    styles = _normalize_styles(intake["styles"])
    gender = intake["gender"].lower()
    fit = (intake.get("fit") or "").lower()
    accessibility = intake.get("accessibility") or {}
    colors = palette["colors"][:3]

    # Per category base keywords
    base = {
        "outer": ["overshirt", "light jacket", "blazer", "shacket"],
        "top1": ["oxford shirt", "knit sweater", "merino sweater", "blouse"],
        "top2": ["shirt", "crewneck", "henley", "blouse"],
        "bottom": ["chino", "trousers", "jeans"],
        "shoes": ["sneakers", "derby", "loafers"],
        "tee": ["heavy cotton t-shirt", "white tee"],
        "accessory": ["leather belt", "scarf", "beanie"]
    }

    # Style modifiers
    style_mod = {
        "minimalistisch": {"outer": ["unstructured", "clean"], "bottom": ["tapered"], "shoes": ["minimal"]},
        "casual": {"outer": ["overshirt"], "bottom": ["jeans", "chino"], "shoes": ["sneakers"]},
        "klassiek": {"outer": ["blazer"], "bottom": ["chino"], "shoes": ["derby", "loafer"]},
        "sportief": {"outer": ["track jacket"], "bottom": ["joggers"], "shoes": ["trainers", "running"]},
        "creatief": {"outer": ["pattern"], "accessory": ["accent color"]}
    }

    # Accessibility filters
    acc_words = []
    if accessibility.get("easy_closures"):
        acc_words += ["magnetic", "snap", "easy closure"]
    if accessibility.get("elastic_waist") or accessibility.get("pull_on"):
        acc_words += ["elastic waist", "pull-on"]
    if accessibility.get("soft_fabrics"):
        acc_words += ["soft", "brushed", "stretch"]

    # Gender nuance
    gender_terms = {
        "male": ["men", "heren"],
        "female": ["women", "dames"],
        "unisex": ["unisex"],
        "non-binary": ["unisex"]
    }
    gterms = gender_terms.get(gender, ["unisex"])

    # Countries → shops (for query site filters)
    shops = COUNTRY_SHOPS.get(country, COUNTRY_SHOPS.get("NL"))

    queries: Dict[str, List[str]] = {}
    for cat, keywords in base.items():
        terms = keywords[:]
        for s in styles:
            terms += style_mod.get(s, {}).get(cat, [])
        # Prefer one of the palette colors
        color = random.choice(colors)
        core = f"{gterms[0]} {random.choice(terms)} {color}"
        # Build site filters across shops
        site_filters = " OR ".join([f"site:{d}" for d in shops])
        q = f"{core} ({site_filters})"
        if fit:
            q += f" {fit}"
        if acc_words:
            q += " " + " ".join(acc_words)
        queries[cat] = [q]
    return queries

def _serpapi_search(query: str, country: str, api_key: str) -> List[Dict[str, Any]]:
    # Use Google Shopping engine
    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": api_key,
    }
    # Map country to gl/hl rough defaults
    gl_map = {
        "NL": "nl", "BE": "be", "DE": "de", "FR": "fr", "UK": "uk", "GB": "uk",
        "US": "us", "IE": "ie", "ES": "es", "IT": "it", "SE": "se"
    }
    hl_map = {
        "NL": "nl", "BE": "nl", "DE": "de", "FR": "fr", "UK": "en", "GB": "en",
        "US": "en", "IE": "en", "ES": "es", "IT": "it", "SE": "sv"
    }
    params["gl"] = gl_map.get(country.upper(), "nl")
    params["hl"] = hl_map.get(country.upper(), "nl")

    resp = requests.get("https://serpapi.com/search.json", params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("shopping_results", []) or []
    normalized = []
    for r in results:
        item = {
            "title": r.get("title"),
            "price": r.get("price"),
            "extracted_price": r.get("extracted_price"),
            "currency": r.get("currency"),
            "link": r.get("link"),
            "source": r.get("source"),
            "thumbnail": r.get("thumbnail")
        }
        normalized.append(item)
    return normalized

def _demo_search(category: str, intake: Dict[str, Any], palette: Dict[str, Any]) -> List[Dict[str, Any]]:
    # Filter demo items by category, gender relevance, basic style tags, and colors
    gender = intake["gender"].lower()
    styles = _normalize_styles(intake["styles"])
    colors = set([c.lower() for c in palette["colors"]])
    results = []
    for item in DEMO_FALLBACK_ITEMS:
        if item["category"] != category:
            continue
        if item["gender"] not in ("unisex", gender):
            continue
        if styles and len(set(item.get("styles", [])) & set(styles)) == 0:
            continue
        if item.get("color", "").lower() not in colors:
            continue
        results.append(item)
    return results

def _parse_price(value: Any, default: float = 0.0) -> Tuple[float, str]:
    if value is None:
        return (default, "")
    if isinstance(value, (int, float)):
        return (float(value), "")
    # value like "€39.99"
    s = str(value)
    digits = "".join([c if (c.isdigit() or c in ".," ) else "" for c in s])
    digits = digits.replace(",", ".")
    try:
        return (float(digits), "")
    except:
        return (default, "")

def _pick_best(results: List[Dict[str, Any]], price_cap: float) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    if not results:
        return None, None
    scored = []
    for r in results:
        p, _ = _parse_price(r.get("extracted_price") or r.get("price"))
        if p <= price_cap * 1.1:  # allow +10% per beslisregel
            score = 100 - abs(price_cap - p)  # closer to cap is better (quality proxy)
            scored.append((score, p, r))
    if not scored:
        # fallback: pick cheapest
        for r in results:
            p, _ = _parse_price(r.get("extracted_price") or r.get("price"))
            scored.append((0, p, r))
    scored.sort(key=lambda x: (-x[0], x[1]))
    best = scored[0][2]
    # cheaper alternative ~85% of chosen price
    chosen_price, _ = _parse_price(best.get("extracted_price") or best.get("price"))
    cheaper = None
    cheaper_target = chosen_price * 0.85
    for _, p, r in sorted(scored, key=lambda x: x[1]):
        if p <= cheaper_target and r != best:
            cheaper = r
            break
    return best, cheaper

def generate_outfits(intake: Dict[str, Any], config: EngineConfig) -> Dict[str, Any]:
    random.seed(42)  # deterministic for tests
    country = intake["country"].upper()
    currency = _derive_currency(country, intake.get("currency"))
    styles = _normalize_styles(intake["styles"])
    palette = _pick_palette(styles, intake.get("favorite_colors"))
    allocation = _allocate_budget(intake)

    queries = _build_queries(intake, palette)

    selected_items: Dict[str, Dict[str, Any]] = {}
    alternatives: Dict[str, Dict[str, Any]] = {}

    for cat, qlist in queries.items():
        price_cap = allocation.get(cat, 30.0)
        results = []
        if config.mode == "serpapi":
            if not config.serpapi_api_key:
                raise ValueError("SERPAPI mode selected but no API key provided.")
            # Try each query variant, accumulate
            for q in qlist:
                results.extend(_serpapi_search(query=q, country=country, api_key=config.serpapi_api_key))
        else:
            # demo mode
            results = _demo_search(cat, intake, palette)

        best, cheaper = _pick_best(results, price_cap=price_cap)
        if best is None:
            # fallback: create placeholder
            best = {"title": f"Sample {cat}", "price": price_cap, "extracted_price": price_cap, "currency": currency, "link": "#", "source": "demo", "thumbnail": None, "category": cat}
        selected_items[cat] = best
        if cheaper:
            alternatives[cat] = cheaper

    # Compose 3 outfits from 7 items
    items = selected_items
    def item_title(i): return (i.get("title") or "").split("|")[0].strip()

    outfit_templates = [
        ["outer", "top1", "bottom", "shoes", "accessory"],
        ["top2", "bottom", "shoes", "tee"],
        ["outer", "top2", "bottom", "shoes"]
    ]
    outfits = []
    for idx, tpl in enumerate(outfit_templates[:config.outfits_count]):
        oitems = []
        total = 0.0
        for cat in tpl:
            i = items.get(cat)
            if i is None:
                continue
            price = i.get("extracted_price") or i.get("price") or 0.0
            p = price if isinstance(price, (int, float)) else _parse_price(price)[0]
            total += float(p)
            oitems.append({
                "category": cat,
                "title": item_title(i),
                "price": round(float(p), 2),
                "currency": i.get("currency") or currency,
                "link": i.get("link") or "#",
                "image": i.get("thumbnail"),
                "merchant": i.get("source") or "demo",
                "cheaper_alternative": alternatives.get(cat)
            })
        outfits.append({
            "name": f"Outfit {idx+1}",
            "items": oitems,
            "total": round(total, 2),
            "currency": currency
        })

    explanation = (
        f"We kozen een palet rond {', '.join(palette['colors'][:4])}. "
        f"De selectie volgt de stijlen {', '.join(styles)} (≈70%) met een speelse aanvulling (≈30%). "
        f"Budgetbewaking: totaal ≈ €{allocation['_total']:.0f} met ±10% marge per item. "
        "Per item is één goedkoper alternatief toegevoegd waar mogelijk."
    )

    return {
        "palette": palette,
        "allocation": allocation,
        "outfits": outfits,
        "explanation": explanation,
        "independent_note": "Anna is onafhankelijk: geen affiliate inkomsten. Links zijn puur ter gemak.",
        "country": country,
        "currency": currency
    }