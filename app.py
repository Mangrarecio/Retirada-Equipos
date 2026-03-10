import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import textwrap

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
        secrets_dict = st.secrets["gcp_service_account"]
        
        # --- LIMPIEZA ABSOLUTA DE LA CLAVE ---
        # 1. Extraemos la clave y quitamos todo lo que ensucie el código base64
        clave_sucia = secrets_dict["private_key"]
        clave_limpia = clave_sucia.replace("-----BEGIN PRIVATE KEY-----", "")
        clave_limpia = clave_limpia.replace("-----END PRIVATE KEY-----", "")
        clave_limpia = clave_limpia.replace("\\n", "").replace("\n", "").replace(" ", "").replace('"', '').replace("'", "")
        
        # 2. Reconstruimos la clave en bloques exactos de 64 caracteres (lo que exige Google)
        clave_perfecta = "-----BEGIN PRIVATE KEY-----\n" + "\n".join(textwrap.wrap(clave_limpia, 64)) + "\n-----END PRIVATE KEY-----\n"
        
        info_servicio = {
            "type": secrets_dict["type"],
            "project_id": secrets_dict["project_id"],
            "private_key_id": secrets_dict["private_key_id"],
            "private_key": clave_perfecta,  # <-- Usamos la clave reconstruida sin errores
            "client_email": secrets_dict["client_email"],
            "client_id": secrets_dict["client_id"],
            "auth_uri": secrets_dict["auth_uri"],
            "token_uri": secrets_dict["token_uri"],
            "auth_provider_x509_cert_url": secrets_dict["auth_provider_x509_cert_url"],
            "client_x509_cert_url": secrets_dict["client_x509_cert_url"],
        }
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credenciales = Credentials.from_service_account_info(info_servicio, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        return cliente.open("Retirada Equipos").sheet1
    
    except Exception as e:
        st.error(f"Error detallado: {e}")
        return None

def guardar_datos(tipo, fecha, enfermero_dni, equipo, lugar, celador_dni):
    hoja = conectar_google_sheets()
    if hoja:
        try:
            fila = [tipo, fecha.strftime("%d/%m/%Y"), enfermero_dni, equipo, lugar, celador_dni]
            hoja.append_row(fila)
            return True
        except Exception as e:
            st.error(f"Error al escribir: {e}")
    return False

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("Acceso")
    password = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        if password == "@1357#":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Incorrecto")
    st.stop()

# --- APP ---
st.title("Gestión Retirada De Equipos")
tab1, tab2 = st.tabs(["🔴 RETIRADA", "🟢 ENTREGA"])

with tab1:
    with st.form("f1", clear_on_submit=True):
        f = st.date_input("Fecha")
        enf = st.text_input("Enfermero y DNI")
        eq = st.text_input("Equipo")
        lug = st.text_input("Lugar")
        cel = st.text_input("Celador y DNI")
        if st.form_submit_button("Registrar"):
            if all([enf, eq, lug, cel]):
                if guardar_datos("RETIRADA", f, enf, eq, lug, cel):
                    st.success("Guardado correctamente en la hoja de cálculo")
            else:
                st.warning("Completa todos los campos")

with tab2:
    with st.form("f2", clear_on_submit=True):
        f2 = st.date_input("Fecha")
        enf2 = st.text_input("Enfermero y DNI")
        eq2 = st.text_input("Equipo")
        lug2 = st.text_input("Lugar")
        cel2 = st.text_input("Celador y DNI")
        if st.form_submit_button("Registrar"):
            if all([enf2, eq2, lug2, cel2]):
                if guardar_datos("ENTREGA", f2, enf2, eq2, lug2, cel2):
                    st.success("Guardado correctamente en la hoja de cálculo")
            else:
                st.warning("Completa todos los campos")