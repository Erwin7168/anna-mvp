/** Anna MVP front-end — altijd LIVE via SerpAPI + moduslabel **/

const qs = (sel, el=document) => el.querySelector(sel);
const qsa = (sel, el=document) => [...el.querySelectorAll(sel)];

const state = {
  step: 0,
  intake: {
    purpose: "",
    styles: [],
    gender: "unisex",
    fit: "",
    age_range: "",
    country: "NL",
    budget_total: 250,
    budget_per_item: null,
    sizes: {},
    favorite_colors: [],
    materials_avoid: [],
    accessibility: {},
    sustainability_preference: false,
    currency: "EUR"
  },
  apiBase: localStorage.getItem("apiBase") || "https://anna-mvp.onrender.com",
  hasSerpEnv: false, // alleen voor info
};

const BUBBLE = qs("#bubbleTemplate").content.firstElementChild;

function addBubble(text, who="anna"){
  const bubble = BUBBLE.cloneNode(true);
  bubble.classList.add(who);
  bubble.querySelector("p").innerHTML = text;
  qs("#chat").appendChild(bubble);
  bubble.scrollIntoView({behavior:"smooth", block:"end"});
}

function addUser(text){ addBubble(text, "user"); }

async function fetchMeta(){
  try{
    const res = await fetch(state.apiBase + "/api/meta");
    const data = await res.json();
    state.hasSerpEnv = !!data.has_serpapi;
  }catch(e){
    state.hasSerpEnv = false;
  }
}

function showQuestion(){
  const s = state.step;
  switch(s){
    case 0: break;
    case 1:
      addBubble("Kies 1–2 stijlen: <em>minimalistisch</em>, <em>casual</em>, <em>klassiek</em>, <em>sportief</em>, <em>creatief</em>.");
      break;
    case 2:
      addBubble("Welke gender/pasvorm wil je dat ik aanhoud? Typ bijv. <em>male recht</em> of <em>female relaxed</em>. Laat leeg = unisex.");
      break;
    case 3:
      addBubble("Welke leeftijdscategorie? 18–25 / 26–35 / 36–45 / 46–55 / 56+.");
      break;
    case 4:
      addBubble("In welk land bestel je? (bijv. NL, BE, DE, FR, UK, US).");
      break;
    case 5:
      addBubble("Wat is je <strong>totaalbudget</strong>? Typ een bedrag, bijv. 250.");
      break;
    case 6:
      addBubble("Wat zijn je maten? Typ bijv. <em>broekmaat 50</em>, <em>bovenmaat L</em>, <em>schoenmaat 43</em>. Of zeg <em>skip</em>.");
      break;
    case 7:
      addBubble("Favoriete kleuren (optioneel)? Typ 1–3, bv. <em>navy, olijf, wit</em>. Of zeg <em>skip</em>.");
      break;
    case 8:
      addBubble("Toegankelijkheidswensen (optioneel): typ woorden zoals <em>elastic waist</em>, <em>soft fabrics</em>, <em>easy closures</em>. Of <em>skip</em>.");
      break;
    case 9:
      addBubble("Top! Zal ik nu 3 outfits genereren? Typ <strong>ja</strong> om te starten.");
      break;
    default: break;
  }
}

function parseInput(text){
  const s = state.step;
  const t = text.trim();
  if(!t) return;

  switch(s){
    case 0:
      state.intake.purpose = t.toLowerCase();
      addUser(text); state.step++; showQuestion(); break;

    case 1:
      addUser(text);
      let styles = t.toLowerCase().split(/[,\s]+/).filter(Boolean);
      styles = styles.filter(x => ["minimalistisch","casual","klassiek","sportief","creatief"].includes(x));
      if(styles.length === 0) styles = ["casual"];
      state.intake.styles = styles.slice(0,2);
      state.step++; showQuestion(); break;

    case 2:
      addUser(text);
      if(t.toLowerCase() !== "skip"){
        const parts = t.toLowerCase().split(/\s+/);
        state.intake.gender = ["male","female","unisex","non-binary"].includes(parts[0]) ? parts[0] : "unisex";
        state.intake.fit = parts[1] || "";
      }
      state.step++; showQuestion(); break;

    case 3:
      addUser(text); state.intake.age_range = t; state.step++; showQuestion(); break;

    case 4:
      addUser(text); state.intake.country = t.toUpperCase(); state.step++; showQuestion(); break;

    case 5:
      addUser(text);
      const num = parseFloat(t.replace(",", "."));
      state.intake.budget_total = isNaN(num) ? 250 : num;
      state.step++; showQuestion(); break;

    case 6: // maten
      addUser(text);
      if(t.toLowerCase() !== "skip"){
        const sizes = {};
        const lower = t.toLowerCase();
        const broek = lower.match(/broek\w*\D+(\d{2,3}(?:\/\d{2})?)/);
        if(broek) sizes.bottom = broek[1];
        const boven = lower.match(/boven\w*\D+\b(xs|s|m|l|xl|xxl)\b/);
        if(boven) sizes.top = boven[1].toUpperCase();
        const schoen = lower.match(/schoen\w*\D+(\d{2,3})/);
        if(schoen) sizes.shoes = schoen[1];
        if(!sizes.top){
          const loneTop = lower.match(/\b(xs|s|m|l|xl|xxl)\b/);
          if(loneTop) sizes.top = loneTop[1].toUpperCase();
        }
        state.intake.sizes = sizes;
      }
      state.step++; showQuestion(); break;

    case 7:
      addUser(text);
      if(t.toLowerCase() !== "skip"){
        state.intake.favorite_colors = t.split(",").map(s => s.trim().toLowerCase()).slice(0,3);
      }
      state.step++; showQuestion(); break;

    case 8:
      addUser(text);
      if(t.toLowerCase() !== "skip"){
        const flags = {
          "elastic waist": "elastic_waist",
          "easy closures": "easy_closures",
          "soft fabrics": "soft_fabrics",
          "pull-on": "pull_on",
          "pull on": "pull_on",
        };
        state.intake.accessibility = {};
        Object.entries(flags).forEach(([k,v]) => {
          if(t.toLowerCase().includes(k)) state.intake.accessibility[v] = true;
        });
      }
      state.step++; showQuestion(); break;

    case 9:
      addUser(text);
      if(t.toLowerCase().startsWith("j")) generateOutfits();
      else addBubble("Geen probleem. Zeg het als je klaar bent met <strong>ja</strong>.");
      break;

    default:
      addUser(text);
  }
}

async function generateOutfits(){
  addBubble("Top — ik ga voor je aan de slag ✅ Een momentje…");
  try{
    const res = await fetch(state.apiBase + "/api/generate", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({
        intake: state.intake,
        mode: "serpapi",       // altijd LIVE
        serpapi_api_key: null, // sleutel staat server-side
        outfits_count: 3
      })
    });
    if(!res.ok){
      const err = await res.json().catch(()=>({detail: res.statusText}));
      throw new Error(err.detail || "Onbekende fout");
    }
    const data = await res.json();
    renderOutfits(data, "live via SerpAPI");
  }catch(e){
    addBubble("Hm, dat ging mis. Probeer later opnieuw.", "anna");
  }
}

function renderOutfits(data, modeLabel="live"){
  const chat = qs("#chat");
  const wrap = document.createElement("div");
  wrap.className = "outfits";

  // Moduslabel
  const badge = document.createElement("div");
  badge.className = "small";
  badge.style.margin = "6px 0 8px 0";
  badge.style.opacity = "0.8";
  badge.textContent = `modus: ${modeLabel}`;
  chat.appendChild(badge);

  data.outfits.forEach(out => {
    const card = document.createElement("div");
    card.className = "card";
    const h3 = document.createElement("h3");
    h3.textContent = out.name;
    card.appendChild(h3);

    out.items.forEach(it => {
      const row = document.createElement("div");
      row.className = "item";
      const img = document.createElement("img");
      img.alt = it.title;
      img.src = it.image || "data:image/svg+xml;charset=utf-8," + encodeURIComponent(`<svg xmlns='http://www.w3.org/2000/svg' width='64' height='64'><rect width='100%' height='100%' fill='#1f2330'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' fill='#aab1c7' font-size='10'>item</text></svg>`);
      const col = document.createElement("div");
      const title = document.createElement("div");
      title.innerHTML = `<strong>${escapeHtml(it.title)}</strong> <span class="label">(${it.category})</span>`;
      const meta = document.createElement("div");
      meta.className = "small";
      const merchant = it.merchant ? ` • ${escapeHtml(it.merchant)}` : "";
      const link = it.link || "#";
      meta.innerHTML = `${formatPrice(it.price, it.currency)}${merchant} — <a href="${link}" target="_blank" rel="noopener">bekijk</a>`;
      col.appendChild(title);
      col.appendChild(meta);
      row.appendChild(img);
      row.appendChild(col);
      card.appendChild(row);
    });

    const total = document.createElement("div");
    total.className = "total";
    total.innerHTML = `<span class="label">Totaal</span><strong>${formatPrice(out.total, out.currency)}</strong>`;
    card.appendChild(total);

    wrap.appendChild(card);
  });

  chat.appendChild(wrap);
  wrap.scrollIntoView({behavior:"smooth", block:"end"});

  addBubble(`Waarom dit werkt: ${escapeHtml(data.explanation)}`, "anna");
  addBubble(`Palet: ${data.palette.colors.slice(0,4).join(", ")}.`, "anna");
  addBubble(`Onthoud: ik ben onafhankelijk — geen affiliate of commissies.`, "anna");
}

function formatPrice(value, currency="EUR"){
  try{
    return new Intl.NumberFormat('nl-NL', {style:'currency', currency}).format(value);
  }catch(e){
    return `${value} ${currency}`;
  }
}

function escapeHtml(str){
  return String(str).replace(/[&<>"']/g, m => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[m]));
}

// Input handling
qs("#inputForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const val = qs("#userInput").value;
  if(!val.trim()) return;
  parseInput(val);
  qs("#userInput").value = "";
});

// Settings modal (SERPAPI veld wordt uitgezet)
const modal = qs("#settingsModal");
qs("#settingsBtn").addEventListener("click", () => {
  modal.classList.remove("hidden");
  qs("#apiBase").value = state.apiBase;
  const keyInput = qs("#serpKey");
  if (keyInput){
    keyInput.value = "";
    keyInput.disabled = true;
    keyInput.placeholder = "Server-side geregeld (uitgezet)";
    keyInput.title = "De sleutel staat veilig op de server";
  }
});
qs("#closeSettings").addEventListener("click", () => modal.classList.add("hidden"));
qs("#saveSettings").addEventListener("click", () => {
  state.apiBase = qs("#apiBase").value || state.apiBase;
  localStorage.setItem("apiBase", state.apiBase);
  modal.classList.add("hidden");
  addBubble("Instellingen opgeslagen ✅", "anna");
});

// Boot
(async function init(){
  await fetchMeta();
  showQuestion();
})();
