import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Retirada De Equipos", layout="centered")

# Estilos CSS
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    p, label, .stMarkdown, .stButton { font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        # Cargamos los secretos
        s = st.secrets["gcp_service_account"]
        
        # LIMPIEZA DEFINITIVA: Quitamos saltos de línea literales y espacios
        pk = s["private_key"].replace("\\n", "\n").strip()
        
        info_servicio = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s["auth_uri"],
            "token_uri": s["token_uri"],
            "auth_provider_x509_cert_url": s["auth_provider_x509_cert_url"],
            "client_x509_cert_url": s["client_x509_cert_url"],
        }
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credenciales = Credentials.from_service_account_info(info_servicio, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        
        # Intenta abrir la hoja
        return cliente.open("Retirada Equipos").sheet1
    
    except Exception as e:
        st.error(f"Error detallado de conexión: {e}")
        return None

def guardar_datos(tipo, fecha, enf, eq, lug, cel):
    hoja = conectar_google_sheets()
    if hoja:
        try:
            fila = [tipo, fecha.strftime("%d/%m/%Y"), enf, eq, lug, cel]
            hoja.append_row(fila)
            return True
        except Exception as e:
            st.error(f"Error al escribir: {e}")
    return False

# --- ACCESO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("Acceso")
    pwd = st.text_input("Clave de seguridad", type="password")
    if st.button("Entrar"):
        if pwd == "@1357#":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Incorrecta")
    st.stop()

# --- FORMULARIOS ---
st.title("Gestión Retirada De Equipos")
t1, t2 = st.tabs(["🔴 RETIRADA", "🟢 ENTREGA"])

with t1:
    with st.form("f1", clear_on_submit=True):
        f = st.date_input("Fecha", key="d1")
        en = st.text_input("Enfermero y DNI", key="e1")
        eq = st.text_input("Equipo", key="eq1")
        lu = st.text_input("Lugar", key="l1")
        ce = st.text_input("Celador y DNI", key="c1")
        if st.form_submit_button("Registrar Retirada"):
            if all([en, eq, lu, ce]):
                if guardar_datos("RETIRADA", f, en, eq, lu, ce):
                    st.success("Registrado con éxito")

with t2:
    with st.form("f2", clear_on_submit=True):
        f2 = st.date_input("Fecha", key="d2")
        en2 = st.text_input("Enfermero y DNI", key="e2")
        eq2 = st.text_input("Equipo", key="eq2")
        lu2 = st.text_input("Lugar", key="l2")
        ce2 = st.text_input("Celador y DNI", key="c2")
        if st.form_submit_button("Registrar Entrega"):
            if all([en2, eq2, lu2, ce2]):
                if guardar_datos("ENTREGA", f2, en2, eq2, lu2, ce2):
                    st.success("Registrado con éxito")