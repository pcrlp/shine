import streamlit as st
import requests
import os
import unicodedata
from datetime import datetime, timezone, timedelta

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

BRT = timezone(timedelta(hours=-3))

def strip_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 0.8rem; padding-bottom: 0.5rem; max-width: 500px;}
html, body, [data-testid="stAppViewContainer"] { font-family: 'Poppins', sans-serif; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(165deg, #8B3A4A 0%, #A0505E 30%, #B8736D 60%, #D4A574 100%);
}
[data-testid="stHeader"] { background: transparent; }

/* Title - compact */
.shine-title { text-align: center; padding: 0.4rem 0 0.1rem 0; }
.shine-title h1 { font-weight: 300; font-size: 1.4rem; color: #FFECD2; margin: 0; letter-spacing: 2px; }
.shine-title h2 { font-weight: 700; font-size: 1.8rem; color: #FFD7A8; margin: -0.1rem 0 0 0; text-shadow: 0 0 20px rgba(255,215,168,0.4); }
.shine-title p { font-size: 0.75rem; color: #D4B8A0; margin: 0; letter-spacing: 1px; }

/* Stats - compact */
.stats-bar { display: flex; justify-content: space-around; background: rgba(255,255,255,0.1); border-radius: 12px; padding: 0.5rem 0.3rem; margin: 0.4rem 0; }
.stat-item { text-align: center; }
.stat-number { font-size: 1.3rem; font-weight: 700; color: #FFD7A8; }
.stat-label { font-size: 0.6rem; color: #E8C8B0; text-transform: uppercase; letter-spacing: 1px; }

/* Search bar */
[data-testid="stTextInput"] > div { background: transparent !important; }
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.92) !important;
    border: 1px solid rgba(200,180,170,0.4) !important;
    border-radius: 12px !important;
    color: #4A2A30 !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1rem !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
}
[data-testid="stTextInput"] input::placeholder { color: #9A7A70 !important; }
[data-testid="stTextInput"] label { display: none !important; }

/* Select / dropdown filter */
[data-testid="stSelectbox"] > div { background: transparent !important; }
[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,236,210,0.3) !important;
    border-radius: 10px !important;
    color: #FFECD2 !important;
    font-size: 0.85rem !important;
}
[data-testid="stSelectbox"] label { display: none !important; }
[data-testid="stSelectbox"] svg { fill: #FFD7A8 !important; }

/* ── Person row: ALL IN ONE LINE ── */
.p-row {
    display: flex;
    align-items: center;
    background: rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 0.5rem 0.6rem;
    margin: 0.25rem 0;
    gap: 0.4rem;
}
.p-row.done {
    background: rgba(255,215,168,0.18);
    border-left: 3px solid #FFD7A8;
}
.p-row .name {
    flex: 1;
    color: #FFECD2;
    font-size: 0.85rem;
    font-weight: 400;
    line-height: 1.2;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
}
.p-row.done .name { color: #FFD7A8; font-weight: 500; }
.p-row .time {
    color: #D4B8A0;
    font-size: 0.6rem;
}
.p-row .ok-icon {
    width: 28px; height: 28px;
    border-radius: 50%;
    background: #2ECDA7;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.p-row .ok-icon svg { width: 16px; height: 16px; }

/* ── Button: compact pill INSIDE the row ── */
[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 0 !important;
    align-items: stretch !important;
}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child {
    flex: 1 !important;
    min-width: 0 !important;
}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child {
    max-width: 90px !important;
    min-width: 80px !important;
    display: flex; align-items: center; justify-content: center;
}
.stButton > button {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.6rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.3px !important;
    padding: 0.35rem 0.6rem !important;
    border-radius: 20px !important;
    min-height: 0 !important;
    line-height: 1 !important;
    white-space: nowrap !important;
    background: transparent !important;
    color: #FFD7A8 !important;
    border: 1.5px solid #FFD7A8 !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: rgba(255,215,168,0.2) !important;
}

hr { border-color: rgba(255,236,210,0.1) !important; margin: 0.3rem 0 !important; }
.no-results { color: #D4B8A0; text-align: center; font-size: 0.9rem; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── JS: instant search ──
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
        }, 350);
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

def do_checkin(record_id):
    now = datetime.now(BRT).isoformat()
    requests.patch(
        f"{API}/checkin?id=eq.{record_id}",
        headers=HEADERS,
        json={"checked_in": True, "checked_at": now},
    ).raise_for_status()

def undo_checkin(record_id):
    requests.patch(
        f"{API}/checkin?id=eq.{record_id}",
        headers=HEADERS,
        json={"checked_in": False, "checked_at": None},
    ).raise_for_status()

def format_time(iso_str):
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d/%m %H:%M")
    except:
        return ""

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

search = st.text_input("Buscar", placeholder="🔍  Digite nome ou sobrenome...")

filtro = st.selectbox("Filtro", [
    f"Todas ({total})",
    f"Chegaram ({arrived})",
    f"Faltam ({missing})",
], label_visibility="collapsed")

st.markdown("---")

# Apply filter
data = all_data
if filtro.startswith("Chegaram"):
    data = [d for d in data if d.get("checked_in")]
elif filtro.startswith("Faltam"):
    data = [d for d in data if not d.get("checked_in")]

# Apply search
if search:
    term = strip_accents(search.strip().lower())
    data = [d for d in data if term in strip_accents(d["nome"].lower())]

if not data and total > 0:
    st.markdown('<p class="no-results">Nenhum resultado.</p>', unsafe_allow_html=True)
elif total == 0:
    st.markdown('<p class="no-results">Nenhuma inscrita carregada.</p>', unsafe_allow_html=True)

CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'

for person in data:
    pid = person["id"]
    name = person["nome"]
    checked = person.get("checked_in", False)
    checked_at = person.get("checked_at", None)

    col1, col2 = st.columns([5, 2])

    with col1:
        cls = "p-row done" if checked else "p-row"
        icon = f'<div class="ok-icon">{CHECK_SVG}</div>' if checked else ""
        time_str = f'<div class="time">✓ {format_time(checked_at)}</div>' if checked and checked_at else ""
        st.markdown(
            f'<div class="{cls}">'
            f'  <div style="flex:1;min-width:0"><div class="name">{name}</div>{time_str}</div>'
            f'  {icon}'
            f'</div>',
            unsafe_allow_html=True
        )

    with col2:
        if checked:
            if st.button("DESFAZER", key=f"b_{pid}"):
                undo_checkin(pid)
                st.rerun()
        else:
            if st.button("CHECK-IN", key=f"b_{pid}"):
                do_checkin(pid)
                st.rerun()
