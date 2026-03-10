import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import re

# --- INTERFAZ LIMPIA (OCULTA BARRA SUPERIOR Y MENÚS) ---
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

def conectar_google_sheets():
    try:
        s = st.secrets["gcp_service_account"]
        
        # --- LIMPIEZA RADICAL DE BYTES INVISIBLES (\x91, \x8d, etc.) ---
        pk_raw = s["private_key"]
        
        # 1. Quitamos los encabezados para limpiar solo el centro
        pk_body = pk_raw.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        
        # 2. FILTRO ANTI-BASURA: Solo permite caracteres Base64 (A-Z, a-z, 0-9, +, /, =)
        # Esto borra automáticamente el byte \x91 y cualquier otro símbolo oculto.
        pk_clean = re.sub(r'[^A-Za-z0-9+/=]', '', pk_body)
        
        # 3. Ajuste de Padding (Relleno de seguridad)
        while len(pk_clean) % 4 != 0:
            pk_clean += '='
            
        # 4. Reconstrucción con el formato oficial
        pk_final = f"-----BEGIN PRIVATE KEY-----\n{pk_clean}\n-----END PRIVATE KEY-----\n"
        
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
        
        # ID de tu hoja confirmado
        id_hoja = "1mcCAwKfy84oBQnpaJWGodR8KL8BQX-QQmiYA1Hdl3DM"
        return cliente.open_by_key(id_hoja).sheet1
        
    except Exception as e:
        st.error(f"Error de acceso: {e}")
        return None

# --- LÓGICA DE ACCESO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Acceso al Sistema")
    pwd = st.text_input("Introduzca Clave de Seguridad", type="password")
    if st.button("Acceder"):
        if pwd == "@1357#":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave Incorrecta")
    st.stop()

# --- APLICACIÓN ---
st.title("Gestión de Equipos")
t1, t2 = st.tabs(["🔴 REGISTRAR RETIRADA", "🟢 REGISTRAR ENTREGA"])

def enviar_datos(datos):
    with st.spinner('Registrando en la base de datos...'):
        hoja = conectar_google_sheets()
        if hoja:
            hoja.append_row(datos)
            return True
    return False

with t1:
    with st.form("form_retirada", clear_on_submit=True):
        f = st.date_input("Fecha", value=datetime.date.today())
        en = st.text_input("Nombre Enfermero / DNI")
        eq = st.text_input("Identificación Equipo")
        lu = st.text_input("Lugar / Servicio")
        ce = st.text_input("Nombre Celador / DNI")
        if st.form_submit_button("REGISTRAR RETIRADA"):
            if all([en, eq, lu, ce]):
                if enviar_datos(["RETIRADA", f.strftime("%d/%m/%Y"), en, eq, lu, ce]):
                    st.success("✅ Guardado correctamente en Drive.")
            else:
                st.warning("Debe rellenar todos los campos.")

with t2:
    with st.form("form_entrega", clear_on_submit=True):
        f2 = st.date_input("Fecha", value=datetime.date.today())
        en2 = st.text_input("Nombre Enfermero / DNI")
        eq2 = st.text_input("Identificación Equipo")
        lu2 = st.text_input("Lugar / Servicio")
        ce2 = st.text_input("Nombre Celador / DNI")
        if st.form_submit_button("REGISTRAR ENTREGA"):
            if all([en2, eq2, lu2, ce2]):
                if enviar_datos(["ENTREGA", f2.strftime("%d/%m/%Y"), en2, eq2, lu2, ce2]):
                    st.success("✅ Guardado correctamente en Drive.")
            else:
                st.warning("Debe rellenar todos los campos.")