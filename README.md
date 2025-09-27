# Anna — Je Virtuele Stijlist (MVP, testversie zonder betaalmuur)

**Tagline:** _“Slim stylen. Nuchter advies. Meteen bestelbaar.”_  
**USP:** Onafhankelijk advies — geen affiliate of commissies.

---

## Wat is dit?
Een minimal viable product van **Anna**, een chatbot die met max. 6 vragen jouw situatie begrijpt en **3 outfits** voor je samenstelt.  
De MVP kan draaien in **demo-modus** (zonder externe koppelingen) of in **live-modus** via **SERPAPI** (Google Shopping) voor echte producten en links.

> ⚠️ In lijn met je strategie is Anna **onafhankelijk**: we gebruiken SERPAPI puur als zoekbron. Geen affiliate, geen commissies.

---

## Snel starten (lokale setup)

### 1) Vereisten
- Python 3.10+

### 2) Backend installeren
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # optioneel, vul je SERPAPI key in
uvicorn main:app --reload
```
Backend draait op **http://localhost:8000**.

### 3) Frontend openen
Open `frontend/index.html` in je browser.  
(Je kunt ook een simpele static server gebruiken, maar dat hoeft niet — het werkt vanaf file://.)

### 4) (Optioneel) SERPAPI live-modus
- Voeg je key toe in `backend/.env` **of** in de frontend via **Instellingen → SERPAPI API key**.
- Zonder key draait de app in **demo-modus** met een kleine voorbeeldcatalogus.

---

## Hoe werkt het?

1. **Intake** (max. 6 stappen): doel, stijl (1–2), gender/pasvorm, leeftijd, land, budget (+ optioneel kleuren en toegankelijkheid).
2. **Beslisregels** (geïmplementeerd):  
   - ~70% volgens gekozen stijl, ~30% speels/aanvullend  
   - Budgetbewaking met ±10% marge per item en **altijd 1 goedkoper alternatief** waar mogelijk  
   - 7 items → **3 outfits** samengesteld
3. **Zoekbron**:  
   - **demo**: interne mini-catalogus (`style_presets.py` → `DEMO_FALLBACK_ITEMS`)  
   - **serpapi**: Google Shopping via SERPAPI (land-specifieke `gl/hl` + `site:domain` filters per land)
4. **Output**: kaarten met items (titel, prijs, merchant, link), totaal per outfit, korte uitleg waarom het werkt + palet.

---

## Onafhankelijkheid (geen affiliate)
- We verdienen niets aan de links. We tonen wat past bij intake/budget.  
- Als je later toch commissies wil, kun je de `link`-velden transformeren — de kernlogica blijft hetzelfde.

---

## Bestanden

- `backend/main.py` — FastAPI app, endpoints:  
  - `GET /api/meta` (controle of SERPAPI key aanwezig is)  
  - `POST /api/generate` (genereert outfits; body bevat intake + mode + optionele key)
- `backend/outfit_engine.py` — kernlogica: palet, budget, querybouw, selectie, combinaties
- `backend/style_presets.py` — stijlpaletten, landen→shops, demo-items
- `backend/requirements.txt` — afhankelijkheden
- `backend/.env.example` — zet hier optioneel je SERPAPI key
- `frontend/index.html` — minimalistische UI (chat + resultaten)
- `frontend/app.js` — intake-flow, API-calls, rendering
- `frontend/styles.css` — donkere, moderne styling

---

## API Voorbeeld

```http
POST /api/generate
Content-Type: application/json

{
  "intake": {
    "purpose": "werk",
    "styles": ["smart-casual", "minimalistisch"],  // NB: UI normaliseert naar geldige labels
    "gender": "male",
    "fit": "recht",
    "age_range": "36–45",
    "country": "NL",
    "budget_total": 250,
    "favorite_colors": ["navy","olijf","wit"],
    "accessibility": {"elastic_waist": true}
  },
  "mode": "demo",           // of "serpapi"
  "serpapi_api_key": null,  // optioneel als .env is gezet
  "outfits_count": 3
}
```

---

## Bekende beperkingen (MVP)
- SERPAPI resultaten kunnen **ruis** bevatten; we filteren op prijs en shop-domeinen per land, maar het blijft een eerste versie.
- Geen retour- of levertijdinformatie (kan later via shop-API’s).
- Maatvoering & voorraad niet gegarandeerd (SERPAPI beperkt dit).

---

## Roadmap suggesties
- Kastfoto-analyse (manueel starten; later vision-model koppelen).
- Per land extra shop-domeinen + handmatige “blocklist” voor lage kwaliteit.
- Optionele “toegankelijkheidsmodus” prominenter in UI.
- Exporteer als PDF/kooplijst in 1 klik.
- Betaalmuur toevoegen (Stripe) zodra je wil monetizen.

---

## Licentie
MIT — gebruik, wijzig en test vrijelijk.