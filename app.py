import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import re

# --- CONFIGURACIÓN E INTERFAZ LIMPIA (SIN BOTÓN DE DEPLOY) ---
st.set_page_config(page_title="Gestión Retirada De Equipos", layout="centered")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    /* Ocultar botón de Deploy y barra superior */
    .stAppDeployButton {display:none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
    
    /* Texto en negrita para mejor lectura */
    p, label, .stMarkdown, .stButton {
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

def conectar_google_sheets():
    try:
        s = st.secrets["gcp_service_account"]
        
        # Limpieza de clave para asegurar conexión
        pk = s["private_key"].replace("\\n", "\n")
        pk = re.sub(r' +', ' ', pk) # Quita espacios dobles
        
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
        
        # Debe ser el nombre exacto de tu archivo en Google Drive
        return cliente.open("Retirada Equipos").sheet1
    except Exception as e:
        # Si llega aquí, es que falta el permiso en el Excel
        st.error("Error: La hoja de cálculo no ha dado acceso a este usuario.")
        st.info(f"Copia este email y dale permiso de EDITOR en tu Excel:\n\n{s['client_email']}")
        return None

# --- RESTO DEL CÓDIGO (Lógica de guardado y formularios) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("Acceso")
    pwd = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if pwd == "@1357#":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Incorrecta")
    st.stop()

st.title("Gestión Retirada De Equipos")
t1, t2 = st.tabs(["🔴 RETIRADA", "🟢 ENTREGA"])

def guardar_datos(datos):
    hoja = conectar_google_sheets()
    if hoja:
        hoja.append_row(datos)
        return True
    return False

with t1:
    with st.form("f1", clear_on_submit=True):
        f = st.date_input("Fecha")
        en = st.text_input("Enfermero y DNI")
        eq = st.text_input("Equipo")
        lu = st.text_input("Lugar")
        ce = st.text_input("Celador y DNI")
        if st.form_submit_button("Registrar"):
            if all([en, eq, lu, ce]):
                if guardar_datos(["RETIRADA", f.strftime("%d/%m/%Y"), en, eq, lu, ce]):
                    st.success("Guardado")

with t2:
    with st.form("f2", clear_on_submit=True):
        f2 = st.date_input("Fecha")
        en2 = st.text_input("Enfermero y DNI")
        eq2 = st.text_input("Equipo")
        lu2 = st.text_input("Lugar")
        ce2 = st.text_input("Celador y DNI")
        if st.form_submit_button("Registrar"):
            if all([en2, eq2, lu2, ce2]):
                if guardar_datos(["ENTREGA", f2.strftime("%d/%m/%Y"), en2, eq2, lu2, ce2]):
                    st.success("Guardado")