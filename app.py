import streamlit as st
import requests 
import pandas as pd
import os

# ── Config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Check-in Shine 2026", page_icon="✨", layout="centered")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Configure SUPABASE_URL e SUPABASE_KEY nas variáveis de ambiente (Secrets).")
    st.stop()

API = f"{SUPABASE_URL}/rest/v1"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ── Theme CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 600px;}
html, body, [data-testid="stAppViewContainer"] { font-family: 'Poppins', sans-serif; }
[data-testid="stAppViewContainer"] {
    background: linear-gradient(165deg, #8B3A4A 0%, #A0505E 30%, #B8736D 60%, #D4A574 100%);
}
[data-testid="stHeader"] { background: transparent; }

.shine-title { text-align: center; padding: 0.6rem 0 0.2rem 0; }
.shine-title h1 { font-family: 'Poppins', sans-serif; font-weight: 300; font-size: 1.6rem; color: #FFECD2; margin: 0; letter-spacing: 2px; }
.shine-title h2 { font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 2rem; color: #FFD7A8; margin: -0.3rem 0 0 0; text-shadow: 0 0 20px rgba(255,215,168,0.4); }
.shine-title p { font-size: 0.75rem; color: #FFECD2AA; margin: 0; letter-spacing: 1px; }

.stats-bar { display: flex; justify-content: space-around; background: rgba(0,0,0,0.2); border-radius: 12px; padding: 0.7rem 0.4rem; margin: 0.6rem 0; backdrop-filter: blur(10px); }
.stat-item { text-align: center; }
.stat-number { font-size: 1.5rem; font-weight: 700; color: #FFD7A8; }
.stat-label { font-size: 0.65rem; color: #FFECD2BB; text-transform: uppercase; letter-spacing: 1px; }

[data-testid="stTextInput"] input { background: rgba(255,255,255,0.12) !important; border: 1px solid rgba(255,236,210,0.25) !important; border-radius: 10px !important; color: #FFECD2 !important; font-family: 'Poppins', sans-serif !important; font-size: 0.95rem !important; padding: 0.6rem 1rem !important; }
[data-testid="stTextInput"] input::placeholder { color: #FFECD2AA !important; }
[data-testid="stTextInput"] label { color: #FFECD2CC !important; font-size: 0.8rem !important; }

.person-row { display: flex; align-items: center; justify-content: space-between; background: rgba(255,255,255,0.08); border-radius: 10px; padding: 0.55rem 0.8rem; margin: 0.3rem 0; }
.person-row:hover { background: rgba(255,255,255,0.14); }
.person-row.checked { background: rgba(255,215,168,0.18); border-left: 3px solid #FFD7A8; }
.person-name { color: #FFECD2; font-size: 0.88rem; font-weight: 400; }
.person-name.checked { color: #FFD7A8; font-weight: 500; }
.badge-ok { background: #FFD7A8; color: #7A3040; font-size: 0.6rem; font-weight: 600; padding: 0.15rem 0.5rem; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.5px; margin-left: 0.5rem; }

.stButton > button { background: rgba(255,215,168,0.2) !important; color: #FFECD2 !important; border: 1px solid rgba(255,236,210,0.3) !important; border-radius: 8px !important; font-family: 'Poppins', sans-serif !important; font-size: 0.8rem !important; padding: 0.35rem 1rem !important; }
.stButton > button:hover { background: rgba(255,215,168,0.35) !important; border-color: #FFD7A8 !important; }

[data-testid="stFileUploader"] { background: rgba(255,255,255,0.06); border-radius: 10px; padding: 0.5rem; }
[data-testid="stFileUploader"] label { color: #FFECD2CC !important; font-size: 0.8rem !important; }
[data-testid="stExpander"] { border: 1px solid rgba(255,236,210,0.15) !important; border-radius: 10px !important; }
[data-testid="stExpander"] summary { color: #FFECD2CC !important; font-size: 0.8rem !important; }
[data-testid="stExpander"] summary span { color: #FFECD2CC !important; }
hr { border-color: rgba(255,236,210,0.15) !important; }
</style>
""", unsafe_allow_html=True)

# ── Supabase REST helpers ───────────────────────────────────────────
def load_all():
    r = requests.get(f"{API}/checkin?order=nome.asc", headers=HEADERS)
    r.raise_for_status()
    return r.json()

def toggle_checkin(record_id, new_val):
    r = requests.patch(
        f"{API}/checkin?id=eq.{record_id}",
        headers=HEADERS,
        json={"checked_in": new_val},
    )
    r.raise_for_status()

def upload_names(df):
    requests.delete(f"{API}/checkin?id=gt.0", headers=HEADERS)
    records = [{"nome": str(n).strip(), "checked_in": False} for n in df.iloc[:, 0] if str(n).strip()]
    for i in range(0, len(records), 100):
        requests.post(f"{API}/checkin", headers=HEADERS, json=records[i:i + 100])

def has_any_checkin(data):
    return any(d.get("checked_in") for d in data)

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

locked = has_any_checkin(all_data)

with st.expander("📋 Carregar lista de inscritas" if not locked else "🔒 Lista bloqueada (check-in iniciado)"):
    if locked:
        st.caption("Não é possível substituir a lista após o início do check-in.")
    else:
        uploaded = st.file_uploader("Envie .xlsx ou .csv (1 coluna com nomes)", type=["xlsx", "csv"])
        if uploaded:
            try:
                if uploaded.name.endswith(".csv"):
                    df = pd.read_csv(uploaded, header=None)
                else:
                    df = pd.read_excel(uploaded, header=None)
                first = str(df.iloc[0, 0]).strip().lower()
                if first in ("nome", "nomes", "name", "names", "participante"):
                    df = df.iloc[1:]
                st.info(f"{len(df)} nomes encontrados. Confirma o envio?")
                if st.button("✅ Confirmar e carregar"):
                    upload_names(df)
                    st.success("Lista carregada!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler arquivo: {e}")

st.markdown("---")

search = st.text_input("🔍 Buscar por nome ou sobrenome", placeholder="Digite para filtrar...")

data = all_data
if search:
    term = search.strip().lower()
    data = [d for d in data if term in d["nome"].lower()]

if not data and total > 0:
    st.markdown('<p style="color:#FFECD2AA; text-align:center; font-size:0.85rem;">Nenhum resultado encontrado.</p>', unsafe_allow_html=True)
elif total == 0:
    st.markdown('<p style="color:#FFECD2AA; text-align:center; font-size:0.85rem;">Nenhuma inscrita carregada. Use o menu acima para enviar a planilha.</p>', unsafe_allow_html=True)

for person in data:
    pid = person["id"]
    name = person["nome"]
    checked = person.get("checked_in", False)
    row_class = "person-row checked" if checked else "person-row"
    name_class = "person-name checked" if checked else "person-name"

    col1, col2 = st.columns([4, 1])
    with col1:
        badge = ' <span class="badge-ok">✓ ok</span>' if checked else ""
        st.markdown(f'<div class="{row_class}"><span class="{name_class}">{name}{badge}</span></div>', unsafe_allow_html=True)
    with col2:
        label = "↩️" if checked else "✅"
        if st.button(label, key=f"btn_{pid}", help="Desfazer" if checked else "Marcar chegada"):
            toggle_checkin(pid, not checked)
            st.rerun()
