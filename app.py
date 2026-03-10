import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import re

# --- INTERFAZ PROFESIONAL (OCULTA TODO LO DE STREAMLIT) ---
st.set_page_config(page_title="Gestión Retirada De Equipos", layout="centered")

st.markdown("""
    <style>
    /* Ocultar barra superior, menú y botón de Deploy */
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    
    /* Forzar negritas para mejor lectura */
    p, label, .stMarkdown, .stButton { font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

def conectar_google_sheets():
    try:
        s = st.secrets["gcp_service_account"]
        
        # --- LIMPIEZA ANTIVIRAL DE LA CLAVE ---
        pk = s["private_key"]
        
        # 1. Quitamos los encabezados para limpiar el cuerpo
        cuerpo = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        
        # 2. Eliminamos CUALQUIER carácter que no sea Base64 (espacios, saltos, \n, etc.)
        cuerpo_limpio = re.sub(r'[^A-Za-z0-9+/=]', '', cuerpo)
        
        # 3. Reconstruimos el formato oficial que espera Google
        pk_final = f"-----BEGIN PRIVATE KEY-----\n{cuerpo_limpio}\n-----END PRIVATE KEY-----\n"
        
        info_servicio = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk_final,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": s["client_x509_cert_url"]
        }
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credenciales = Credentials.from_service_account_info(info_servicio, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        
        # Tu ID de hoja confirmado
        return cliente.open_by_key("1mcCAwKfy84oBQnpaJWGodR8KL8BQX-QQmiYA1Hdl3DM").sheet1
    except Exception as e:
        st.error(f"Error técnico de acceso: {e}")
        return None

# --- CONTROL DE ACCESO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso al Sistema")
    pwd = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if pwd == "@1357#":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- FORMULARIOS ---
st.title("Gestión de Equipos")
t1, t2 = st.tabs(["🔴 REGISTRAR RETIRADA", "🟢 REGISTRAR ENTREGA"])

def guardar(datos):
    with st.spinner('Guardando...'):
        hoja = conectar_google_sheets()
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
            else:
                st.warning("Completa todos los campos")

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
            else:
                st.warning("Completa todos los campos")