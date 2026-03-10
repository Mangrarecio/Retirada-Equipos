import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import re

# --- INTERFAZ LIMPIA (OCULTA MENÚS Y BOTÓN DE DEPLOY) ---
st.set_page_config(page_title="Gestión Retirada De Equipos", layout="centered")

st.markdown("""
    <style>
    /* Ocultar barra superior, menú lateral y botón de Deploy */
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppDeployButton {display:none !important;}
    [data-testid="stStatusWidget"] {display:none !important;}
    
    /* Forzar que el texto sea legible y en negrita */
    p, label, .stMarkdown, .stButton {
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

def conectar_google_sheets():
    try:
        s = st.secrets["gcp_service_account"]
        
        # --- SOLUCIÓN AL ERROR DE 65 CARACTERES / BASE64 ---
        pk = s["private_key"]
        
        # 1. Quitamos los encabezados
        contenido = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        
        # 2. Filtramos CUALQUIER cosa que no sea un carácter Base64 válido
        # Esto elimina ese carácter "65" extra que está rompiendo la cadena
        contenido_limpio = re.sub(r'[^A-Za-z0-9+/=]', '', contenido)
        
        # 3. Ajustamos el padding (relleno) para que sea múltiplo de 4
        while len(contenido_limpio) % 4 != 0:
            contenido_limpio += '='
            
        # 4. Reconstruimos la clave con formato oficial
        pk_final = f"-----BEGIN PRIVATE KEY-----\n{contenido_limpio}\n-----END PRIVATE KEY-----\n"
        
        info_servicio = {
            "type": s.get("type", "service_account"),
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk_final,
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
        
        # ID de tu hoja de cálculo
        id_hoja = "1mcCAwKfy84oBQnpaJWGodR8KL8BQX-QQmiYA1Hdl3DM"
        return cliente.open_by_key(id_hoja).sheet1
        
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
            st.error("Incorrecta")
    st.stop()

# --- FORMULARIOS ---
st.title("Gestión de Equipos")
t1, t2 = st.tabs(["🔴 REGISTRAR RETIRADA", "🟢 REGISTRAR ENTREGA"])

def enviar_datos(datos):
    with st.spinner('Conectando con la base de datos...'):
        hoja = conectar_google_sheets()
        if hoja:
            hoja.append_row(datos)
            return True
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
                if enviar_datos(["RETIRADA", f.strftime("%d/%m/%Y"), en, eq, lu, ce]):
                    st.success("✅ Datos guardados correctamente")
            else:
                st.warning("Completa todos los campos")

with t2:
    with st.form("ent", clear_on_submit=True):
        f2 = st.date_input("Fecha")
        en2 = st.text_input("Enfermero y DNI")
        eq2 = st.text_input("Equipo")
        lu2 = st.text_input("Lugar")
        ce2 = st.text_input("Celador y DNI")
        if st.form_submit_button("REGISTRAR ENTREGA"):
            if all([en2, eq2, lu2, ce2]):
                if enviar_datos(["ENTREGA", f2.strftime("%d/%m/%Y"), en2, eq2, lu2, ce2]):
                    st.success("✅ Datos guardados correctamente")
            else:
                st.warning("Completa todos los campos")