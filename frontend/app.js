/** Anna MVP front-end (met extra vraag voor maten) **/

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
    sizes: {},   // <-- hier worden de maten opgeslagen
    favorite_colors: [],
    materials_avoid: [],
    accessibility: {},
    sustainability_preference: false,
    currency: "EUR"
  },
  apiBase: localStorage.getItem("apiBase") || "http://localhost:8000",
  serpKey: localStorage.getItem("serpKey") || "",
  hasSerpEnv: false,
};

const BUBBLE = qs("#bubbleTemplate").content.firstElementChild;

function addBubble(text, who="anna"){
  const bubble = BUBBLE.cloneNode(true);
  bubble.classList.add(who);
  bubble.querySelector("p").innerHTML = text;
  qs("#chat").appendChild(bubble);
  bubble.scrollIntoView({behavior:"smooth", block:"end"});
}

function addUser(text){
  addBubble(text, "user");
}

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
    case 0:
      break;
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
    case 6:  // <<-- nieuwe stap voor maten
      addBubble("Wat zijn je maten? Typ bijv. broekmaat 50, bovenmaat L, schoenmaat 43. Of zeg skip.");
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
    default:
      break;
  }
}

function parseInput(text){
  const s = state.step;
  const t = text.trim();
  if(!t) return;

  switch(s){
    case 0:
      state.intake.purpose = t.toLowerCase();
      addUser(text);
      state.step++;
      showQuestion();
      break;
    case 1:
      addUser(text);
      let styles = t.toLowerCase().split(/[,\s]+/).filter(Boolean);
      styles = styles.filter(x => ["minimalistisch","casual","klassiek","sportief","creatief"].includes(x));
      if(styles.length === 0) styles = ["casual"];
      state.intake.styles = styles.slice(0,2);
      state.step++;
      showQuestion();
      break;
    case 2:
      addUser(text);
      if(t.toLowerCase() !== "skip"){
        const parts = t.toLowerCase().split(/\s+/);
        state.intake.gender = ["male","female","unisex","non-binary"].includes(parts[0]) ? parts[0] : "unisex";
        state.intake.fit = parts[1] || "";
      }
      state.step++;
      showQuestion();
      break;
    case 3:
      addUser(text);
      state.intake.age_range = t;
      state.step++;
      showQuestion();
      break;
    case 4:
      addUser(text);
      state.intake.country = t.toUpperCase();
      state.step++;
      showQuestion();
      break;
    case 5:
      addUser(text);
      const num = parseFloat(t.replace(",", "."));
      state.intake.budget_total = isNaN(num) ? 250 : num;
      state.step++;
      showQuestion();
      break;
    case 6:   // nieuwe stap: maten opslaan
      addUser(text);
      if(t.toLowerCase() !== "skip"){
        // simpele parser
        state.intake.sizes = { raw: t };
      }
      state.step++;
      showQuestion();
      break;
    case 7:
      addUser(text);
      if(t.toLowerCase() !== "skip"){
        state.intake.favorite_colors = t.split(",").map(s => s.trim().toLowerCase()).slice(0,3);
      }
      state.step++;
      showQuestion();
      break;
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
      state.step++;
      showQuestion();
      break;
    case 9:
      addUser(text);
      if(t.toLowerCase().startsWith("j")){
        generateOutfits();
      }else{
        addBubble("Geen probleem. Zeg het als je klaar bent met <strong>ja</strong>.");
      }
      break;
    default:
      addUser(text);
  }
}

async function generateOutfits(){
  addBubble("Top — ik ga voor je aan de slag ✅ Een momentje…");
  const mode = (state.serpKey || state.hasSerpEnv) ? "serpapi" : "demo";
  try{
    const res = await fetch(state.apiBase + "/api/generate", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({
        intake: state.intake,
        mode,
        serpapi_api_key: state.serpKey || null,
        outfits_count: 3
      })
    });
    if(!res.ok){
      const err = await res.json().catch(()=>({detail: res.statusText}));
      throw new Error(err.detail || "Onbekende fout");
    }
    const data = await res.json();
    renderOutfits(data);
  }catch(e){
    addBubble("Hm, dat ging mis. Probeer je <em>Instellingen</em> te checken of draai in <em>demo</em>-modus.", "anna");
  }
}

function renderOutfits(data){
  const chat = qs("#chat");
  const wrap = document.createElement("div");
  wrap.className = "outfits";

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
      const merchant = it.merchant ? ` • ${it.merchant}` : "";
      meta.innerHTML = `${formatPrice(it.price, it.currency)}${merchant} — <a href="${it.link}" target="_blank" rel="noopener">bekijk</a>`;
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

qs("#inputForm").addEventListener("submit", (e) => {
  e.preventDefault();
  const val = qs("#userInput").value;
  if(!val.trim()) return;
  parseInput(val);
  qs("#userInput").value = "";
});

const modal = qs("#settingsModal");
qs("#settingsBtn").addEventListener("click", () => {
  modal.classList.remove("hidden");
  qs("#apiBase").value = state.apiBase;
  qs("#serpKey").value = state.serpKey;
});
qs("#closeSettings").addEventListener("click", () => modal.classList.add("hidden"));
qs("#saveSettings").addEventListener("click", () => {
  state.apiBase = qs("#apiBase").value || state.apiBase;
  state.serpKey = qs("#serpKey").value || "";
  localStorage.setItem("apiBase", state.apiBase);
  localStorage.setItem("serpKey", state.serpKey);
  modal.classList.add("hidden");
  addBubble("Instellingen opgeslagen ✅", "anna");
});

(async function init(){
  await fetchMeta();
  showQuestion();
})();
