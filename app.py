import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import re

# --- INTERFAZ LIMPIA (SIN BARRA SUPERIOR NI MENÚS) ---
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
        
        # --- REPARACIÓN DE CLAVE (ANTI-PADDING Y ANTI-BYTES EXTRA) ---
        pk = s["private_key"]
        
        # 1. Extraemos solo el cuerpo de la clave
        cuerpo = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        
        # 2. Limpieza de cualquier carácter que no sea Base64
        cuerpo_limpio = re.sub(r'[^A-Za-z0-9+/=]', '', cuerpo)
        
        # 3. CORRECCIÓN DE PADDING: Aseguramos que la longitud sea múltiplo de 4
        # Esto soluciona el error "Incorrect padding" automáticamente
        while len(cuerpo_limpio) % 4 != 0:
            cuerpo_limpio += '='
            
        # 4. Reconstrucción con el formato que exige Google
        pk_reparada = f"-----BEGIN PRIVATE KEY-----\n{cuerpo_limpio}\n-----END PRIVATE KEY-----\n"
        
        info_servicio = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk_reparada,
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
        
        # ID de tu hoja de cálculo (de tu enlace)
        id_hoja = "1mcCAwKfy84oBQnpaJWGodR8KL8BQX-QQmiYA1Hdl3DM"
        return cliente.open_by_key(id_hoja).sheet1
        
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

# --- FORMULARIOS ---
st.title("Gestión de Equipos")
t1, t2 = st.tabs(["🔴 RETIRADA", "🟢 ENTREGA"])

def guardar(datos):
    with st.spinner('Registrando en Drive...'):
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
                    st.success("✅ Datos guardados")

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
                    st.success("✅ Datos guardados")