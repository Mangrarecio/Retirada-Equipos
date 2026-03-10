import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- INTERFAZ LIMPIA (OCULTA BARRA DE DEPLOY Y MENÚS) ---
st.set_page_config(page_title="Gestión Retirada De Equipos", layout="centered")

st.markdown("""
    <style>
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    p, label, .stMarkdown, .stButton { font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

def conectar():
    try:
        s = st.secrets["gcp_service_account"]
        # Limpieza estándar de saltos de línea
        info = dict(s)
        info["private_key"] = s["private_key"].replace("\\n", "\n")
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        cliente = gspread.authorize(creds)
        
        # Conexión directa por el ID de tu hoja
        return cliente.open_by_key("1mcCAwKfy84oBQnpaJWGodR8KL8BQX-QQmiYA1Hdl3DM").sheet1
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# --- ACCESO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso")
    pwd = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if pwd == "@1357#":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Incorrecta")
    st.stop()

# --- APP PRINCIPAL ---
st.title("Gestión de Equipos")
t1, t2 = st.tabs(["🔴 RETIRADA", "🟢 ENTREGA"])

def guardar(datos):
    hoja = conectar()
    if hoja:
        hoja.append_row(datos)
        return True
    return False

with t1:
    with st.form("f1", clear_on_submit=True):
        f = st.date_input("Fecha", value=datetime.date.today())
        en = st.text_input("Enfermero y DNI")
        eq = st.text_input("Equipo")
        lu = st.text_input("Lugar")
        ce = st.text_input("Celador y DNI")
        if st.form_submit_button("REGISTRAR RETIRADA"):
            if all([en, eq, lu, ce]):
                if guardar(["RETIRADA", f.strftime("%d/%m/%Y"), en, eq, lu, ce]):
                    st.success("✅ Registrado con éxito")

with t2:
    with st.form("f2", clear_on_submit=True):
        f2 = st.date_input("Fecha", value=datetime.date.today())
        en2 = st.text_input("Enfermero y DNI")
        eq2 = st.text_input("Equipo")
        lu2 = st.text_input("Lugar")
        ce2 = st.text_input("Celador y DNI")
        if st.form_submit_button("REGISTRAR ENTREGA"):
            if all([en2, eq2, lu2, ce2]):
                if guardar(["ENTREGA", f2.strftime("%d/%m/%Y"), en2, eq2, lu2, ce2]):
                    st.success("✅ Registrado con éxito")