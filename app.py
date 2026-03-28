import streamlit as st
import requests
import os
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
.shine-title p { font-size: 0.85rem; color: #D4B8A0; margin: 0; letter-spacing: 1px; }

/* Stats */
.stats-bar { display: flex; justify-content: space-around; background: rgba(255,255,255,0.1); border-radius: 14px; padding: 0.8rem 0.4rem; margin: 0.6rem 0; }
.stat-item { text-align: center; }
.stat-number { font-size: 1.6rem; font-weight: 700; color: #FFD7A8; }
.stat-label { font-size: 0.7rem; color: #E8C8B0; text-transform: uppercase; letter-spacing: 1px; }

/* ── Search bar: clean white ── */
[data-testid="stTextInput"] > div { background: transparent !important; }
[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.92) !important;
    border: 1px solid rgba(200,180,170,0.4) !important;
    border-radius: 14px !important;
    color: #4A2A30 !important;
    font-family: 'Poppins', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1.1rem !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08) !important;
}
[data-testid="stTextInput"] input::placeholder { color: #9A7A70 !important; }
[data-testid="stTextInput"] label { display: none !important; }

/* ── Person card ── */
.card {
    background: rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.card.done {
    background: rgba(255,215,168,0.18);
    border-left: 3px solid #FFD7A8;
}
.card .info { flex: 1; }
.card .name {
    color: #FFECD2;
    font-size: 1rem;
    font-weight: 400;
    display: block;
}
.card.done .name { color: #FFD7A8; font-weight: 500; }
.card .time {
    color: #D4B8A0;
    font-size: 0.7rem;
    margin-top: 2px;
}
.card .check-icon {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: #2ECDA7;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; margin-left: 0.6rem;
}
.card .check-icon svg { width: 20px; height: 20px; }

/* ── Buttons: styled as pill ── */
[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    gap: 0 !important;
}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child {
    max-width: 130px !important;
    min-width: 100px !important;
    display: flex; align-items: center; justify-content: center;
}
/* "FAZER CHECK-IN" style button */
.stButton > button {
    font-family: 'Poppins', sans-serif !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    padding: 0.4rem 0.9rem !important;
    border-radius: 25px !important;
    min-height: 0 !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
    transition: all 0.2s !important;
}
/* Default: check-in pill */
.stButton > button {
    background: transparent !important;
    color: #FFD7A8 !important;
    border: 1.5px solid #FFD7A8 !important;
}
.stButton > button:hover {
    background: rgba(255,215,168,0.2) !important;
}

hr { border-color: rgba(255,236,210,0.12) !important; }
.no-results { color: #D4B8A0; text-align: center; font-size: 0.95rem; margin-top: 1.5rem; }
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

search = st.text_input("Buscar", placeholder="🔍  Nome, email, nº do ingresso ou pedido...")

st.markdown("---")

data = all_data
if search:
    term = search.strip().lower()
    data = [d for d in data if term in d["nome"].lower()]

if not data and total > 0:
    st.markdown('<p class="no-results">Nenhum resultado encontrado.</p>', unsafe_allow_html=True)
elif total == 0:
    st.markdown('<p class="no-results">Nenhuma inscrita carregada ainda.</p>', unsafe_allow_html=True)

CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>'

for person in data:
    pid = person["id"]
    name = person["nome"]
    checked = person.get("checked_in", False)
    checked_at = person.get("checked_at", None)

    col1, col2 = st.columns([5, 2])

    with col1:
        card_cls = "card done" if checked else "card"
        time_html = f'<span class="time">✓ {format_time(checked_at)}</span>' if checked and checked_at else ""
        icon_html = f'<div class="check-icon">{CHECK_SVG}</div>' if checked else ""
        st.markdown(
            f'<div class="{card_cls}">'
            f'  <div class="info"><span class="name">{name}</span>{time_html}</div>'
            f'  {icon_html}'
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
