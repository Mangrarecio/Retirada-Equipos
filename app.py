import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import re

# --- CONFIGURACIÓN DE INTERFAZ TOTALMENTE LIMPIA ---
st.set_page_config(page_title="Gestión Retirada De Equipos", layout="centered")

# CSS para eliminar CUALQUIER rastro de los menús de Streamlit y el botón Deploy
st.markdown("""
    <style>
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    div.block-container {padding-top: 2rem;}
    
    /* Texto en negrita para mejor legibilidad */
    p, label, .stMarkdown, .stButton {
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN POR ID (MÉTODO INFALIBLE) ---
def conectar_google_sheets():
    try:
        s = st.secrets["gcp_service_account"]
        
        # Limpieza de la clave privada
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
        
        # USAMOS EL ID QUE ME HAS PASADO (Es el código entre /d/ y /edit)
        id_hoja = "1mcCAwKfy84oBQnpaJWGodR8KL8BQX-QQmiYA1Hdl3DM"
        return cliente.open_by_key(id_hoja).sheet1
        
    except Exception as e:
        st.error(f"Error técnico de acceso: {e}")
        return None

# --- SISTEMA DE ENTRADA ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("Sistema de Gestión")
    pwd = st.text_input("Introduzca Clave de Acceso", type="password")
    if st.button("Acceder"):
        if pwd == "@1357#":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave Incorrecta")
    st.stop()

# --- FORMULARIOS ---
st.title("Gestión de Equipos")
t1, t2 = st.tabs(["🔴 REGISTRAR RETIRADA", "🟢 REGISTRAR ENTREGA"])

def guardar_registro(lista_datos):
    hoja = conectar_google_sheets()
    if hoja:
        try:
            hoja.append_row(lista_datos)
            return True
        except Exception as e:
            st.error(f"Error al escribir datos: {e}")
    return False

with t1:
    with st.form("form_ret", clear_on_submit=True):
        f = st.date_input("Fecha de Retirada", value=datetime.date.today())
        en = st.text_input("Nombre Enfermero / DNI")
        eq = st.text_input("Identificación del Equipo")
        lu = st.text_input("Lugar / Servicio")
        ce = st.text_input("Nombre Celador / DNI")
        if st.form_submit_button("REGISTRAR RETIRADA"):
            if all([en, eq, lu, ce]):
                if guardar_registro(["RETIRADA", f.strftime("%d/%m/%Y"), en, eq, lu, ce]):
                    st.success("✅ Registrado con éxito.")
            else:
                st.warning("Rellene todos los campos.")

with t2:
    with st.form("form_ent", clear_on_submit=True):
        f2 = st.date_input("Fecha de Entrega", value=datetime.date.today())
        en2 = st.text_input("Nombre Enfermero / DNI")
        eq2 = st.text_input("Identificación del Equipo")
        lu2 = st.text_input("Lugar / Servicio")
        ce2 = st.text_input("Nombre Celador / DNI")
        if st.form_submit_button("REGISTRAR ENTREGA"):
            if all([en2, eq2, lu2, ce2]):
                if guardar_registro(["ENTREGA", f2.strftime("%d/%m/%Y"), en2, eq2, lu2, ce2]):
                    st.success("✅ Registrado con éxito.")
            else:
                st.warning("Rellene todos los campos.")