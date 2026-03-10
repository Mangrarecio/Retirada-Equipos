import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- INTERFAZ LIMPIA (SIN BARRA SUPERIOR) ---
st.set_page_config(page_title="Gestión Retirada De Equipos", layout="centered")

st.markdown("""
    <style>
    /* Ocultar menús, barra superior y botones de Streamlit */
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppDeployButton {display:none !important;}
    
    /* Estilo para que el texto sea más legible */
    p, label, .stMarkdown, .stButton {
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN DIRECTA ---
def conectar_google_sheets():
    try:
        s = st.secrets["gcp_service_account"]
        
        # Limpiamos la clave de posibles errores de formato
        pk = s["private_key"].replace("\\n", "\n").strip()
        
        info_servicio = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": s["client_x509_cert_url"],
        }
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credenciales = Credentials.from_service_account_info(info_servicio, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        
        # IMPORTANTE: Asegúrate de que el archivo se llame exactamente así en Drive
        return cliente.open("Retirada Equipos").sheet1
    except Exception as e:
        st.error(f"Error de acceso: Comprueba que el email del servicio tenga permiso de EDITOR.")
        return None

# --- LÓGICA DE LA APP ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso")
    pwd = st.text_input("Clave de seguridad", type="password")
    if st.button("Entrar"):
        if pwd == "@1357#":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- FORMULARIOS ---
st.title("Gestión Retirada De Equipos")
t1, t2 = st.tabs(["🔴 RETIRADA", "🟢 ENTREGA"])

def guardar(datos):
    hoja = conectar_google_sheets()
    if hoja:
        try:
            hoja.append_row(datos)
            return True
        except Exception as e:
            st.error(f"Error al escribir: {e}")
    return False

with t1:
    with st.form("ret", clear_on_submit=True):
        f = st.date_input("Fecha")
        en = st.text_input("Enfermero y DNI")
        eq = st.text_input("Equipo")
        lu = st.text_input("Lugar")
        ce = st.text_input("Celador y DNI")
        if st.form_submit_button("REGISTRAR RETIRADA"):
            if all([en, eq, lu, ce]):
                if guardar(["RETIRADA", f.strftime("%d/%m/%Y"), en, eq, lu, ce]):
                    st.success("✅ Registrado con éxito")

with t2:
    with st.form("ent", clear_on_submit=True):
        f2 = st.date_input("Fecha")
        en2 = st.text_input("Enfermero y DNI")
        eq2 = st.text_input("Equipo")
        lu2 = st.text_input("Lugar")
        ce2 = st.text_input("Celador y DNI")
        if st.form_submit_button("REGISTRAR ENTREGA"):
            if all([en2, eq2, lu2, ce2]):
                if guardar(["ENTREGA", f2.strftime("%d/%m/%Y"), en2, eq2, lu2, ce2]):
                    st.success("✅ Registrado con éxito")