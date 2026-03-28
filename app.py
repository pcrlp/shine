import streamlit as st
import requests
import os

st.set_page_config(page_title="Check-in Shine 2026", page_icon="✨", layout="centered")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Configure SUPABASE_URL e SUPABASE_KEY nos Secrets.")
    st.stop()

API = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 640px;}
html, body, [data-testid="stAppViewContainer"] { font-family: 'Poppins', sans-serif; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(165deg, #8B3A4A 0%, #A0505E 30%, #B8736D 60%, #D4A574 100%);
}
[data-testid="stHeader"] { background: transparent; }

/* Title */
.shine-title { text-align: center; padding: 0.6rem 0 0.2rem 0; }
.shine-title h1 { font-weight: 300; font-size: 1.8rem; color: #FFECD2; margin: 0; letter-spacing: 2px; }
.shine-title h2 { font-weight: 700; font-size: 2.2rem; color: #FFD7A8; margin: -0.2rem 0 0 0; text-shadow: 0 0 20px rgba(255,215,168,0.4); }
.shine-title p { font-size: 0.85rem; color: #FFECD2BB; margin: 0; letter-spacing: 1px; }

/* Stats */
.stats-bar { display: flex; justify-content: space-around; background: rgba(0,0,0,0.2); border-radius: 12px; padding: 0.8rem 0.4rem; margin: 0.6rem 0; backdrop-filter: blur(10px); }
.stat-item { text-align: center; }
.stat-number { font-size: 1.6rem; font-weight: 700; color: #FFD7A8; }
.stat-label { font-size: 0.7rem; color: #FFECD2BB; text-transform: uppercase; letter-spacing: 1px; }

/* Search input */
[data-testid="stTextInput"] input { background: rgba(255,255,255,0.12) !important; border: 1px solid rgba(255,236,210,0.3) !important; border-radius: 12px !important; color: #FFECD2 !important; font-family: 'Poppins', sans-serif !important; font-size: 1.05rem !important; padding: 0.7rem 1rem !important; }
[data-testid="stTextInput"] input::placeholder { color: #FFECD2AA !important; }
[data-testid="stTextInput"] label { display: none !important; }

/* Person card */
.person-card {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(255,255,255,0.08); border-radius: 12px;
    padding: 0.7rem 1rem; margin: 0.35rem 0;
    min-height: 48px;
}
.person-card.checked {
    background: rgba(255,215,168,0.15); border-left: 3px solid #FFD7A8;
}
.person-card .name {
    color: #FFECD2; font-size: 1rem; font-weight: 400; flex: 1;
}
.person-card.checked .name { color: #FFD7A8; font-weight: 500; }
.person-card .badge {
    background: #FFD7A8; color: #7A3040; font-size: 0.65rem; font-weight: 600;
    padding: 0.2rem 0.6rem; border-radius: 20px; text-transform: uppercase;
    letter-spacing: 0.5px; margin-left: 0.5rem; white-space: nowrap;
}

/* ── FIX: transparent small buttons ── */
[data-testid="stColumn"]:last-child button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 1.4rem !important;
    padding: 0.2rem 0.4rem !important;
    min-height: 0 !important;
    line-height: 1 !important;
}
[data-testid="stColumn"]:last-child button:hover {
    background: rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
}
/* Force columns side by side on mobile */
[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 0 !important;
}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child {
    max-width: 50px !important;
    min-width: 50px !important;
    display: flex; align-items: center; justify-content: center;
}

hr { border-color: rgba(255,236,210,0.15) !important; }
.no-results { color: #FFECD2AA; text-align: center; font-size: 0.95rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── JS: instant search (filter on every keystroke, no Enter needed) ──
st.markdown("""
<script>
const doc = window.parent.document;
function setupInstantSearch() {
    const input = doc.querySelector('[data-testid="stTextInput"] input');
    if (!input || input.dataset.instantBound) return;
    input.dataset.instantBound = 'true';
    let timer = null;
    input.addEventListener('input', function() {
        clearTimeout(timer);
        timer = setTimeout(() => {
            input.dispatchEvent(new Event('change', { bubbles: true }));
            input.blur();
            setTimeout(() => input.focus(), 50);
        }, 300);
    });
}
setTimeout(setupInstantSearch, 500);
new MutationObserver(setupInstantSearch).observe(
    window.parent.document.body, {childList: true, subtree: true}
);
</script>
""", unsafe_allow_html=True)

# ── Helpers ─────────────────────────────────────────────────────────
def load_all():
    r = requests.get(f"{API}/checkin?order=nome.asc", headers=HEADERS)
    r.raise_for_status()
    return r.json()

def toggle_checkin(record_id, new_val):
    requests.patch(
        f"{API}/checkin?id=eq.{record_id}",
        headers=HEADERS,
        json={"checked_in": new_val},
    ).raise_for_status()

# ── UI ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="shine-title">
    <h1>Conferência</h1>
    <h2>✨ Shine 2026</h2>
    <p>Mulheres Conectadas · IBNF</p>
</div>
""", unsafe_allow_html=True)

all_data = load_all()
total = len(all_data)
arrived = sum(1 for d in all_data if d.get("checked_in"))
missing = total - arrived

st.markdown(f"""
<div class="stats-bar">
    <div class="stat-item"><div class="stat-number">{total}</div><div class="stat-label">Inscritas</div></div>
    <div class="stat-item"><div class="stat-number">{arrived}</div><div class="stat-label">Chegaram</div></div>
    <div class="stat-item"><div class="stat-number">{missing}</div><div class="stat-label">Faltam</div></div>
</div>
""", unsafe_allow_html=True)

search = st.text_input("Buscar", placeholder="🔍 Digite nome ou sobrenome para filtrar...")

st.markdown("---")

data = all_data
if search:
    term = search.strip().lower()
    data = [d for d in data if term in d["nome"].lower()]

if not data and total > 0:
    st.markdown('<p class="no-results">Nenhum resultado encontrado.</p>', unsafe_allow_html=True)
elif total == 0:
    st.markdown('<p class="no-results">Nenhuma inscrita carregada ainda.</p>', unsafe_allow_html=True)

for person in data:
    pid = person["id"]
    name = person["nome"]
    checked = person.get("checked_in", False)
    card_cls = "person-card checked" if checked else "person-card"

    col1, col2 = st.columns([6, 1])
    with col1:
        badge = '<span class="badge">✓ chegou</span>' if checked else ""
        st.markdown(f'<div class="{card_cls}"><span class="name">{name}</span>{badge}</div>', unsafe_allow_html=True)
    with col2:
        label = "↩️" if checked else "☐"
        if st.button(label, key=f"b_{pid}"):
            toggle_checkin(pid, not checked)
            st.rerun()
