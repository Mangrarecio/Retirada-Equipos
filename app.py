import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import re

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
        s = st.secrets["gcp_service_account"]
        
        # --- LIMPIEZA DE FUERZA BRUTA ---
        # 1. Extraemos la clave
        pk = s["private_key"]
        
        # 2. Quitamos cabeceras y pies para limpiar el contenido real
        contenido = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        
        # 3. Eliminamos TODO lo que no sea un carácter Base64 válido (letras, números, +, /, =)
        # Esto elimina saltos de línea invisibles, espacios y caracteres basura como \x8d
        contenido_limpio = re.sub(r'[^A-Za-z0-9+/=]', '', contenido)
        
        # 4. Reconstruimos la clave con el formato oficial
        pk_final = f"-----BEGIN PRIVATE KEY-----\n{contenido_limpio}\n-----END PRIVATE KEY-----\n"
        
        info_servicio = {
            "type": s["type"],
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk_final,
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
        
        # Asegúrate de que el nombre coincide con tu Drive
        return cliente.open("Retirada Equipos").sheet1
    
    except Exception as e:
        st.error(f"Error crítico de conexión: {e}")
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

# --- SISTEMA DE ACCESO ---
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
            st.error("Clave incorrecta")
    st.stop()

# --- INTERFAZ ---
st.title("Gestión Retirada De Equipos")
t1, t2 = st.tabs(["🔴 RETIRADA", "🟢 ENTREGA"])

with t1:
    with st.form("f1", clear_on_submit=True):
        f = st.date_input("Fecha", key="d1")
        en = st.text_input("Enfermero y DNI", key="e1")
        eq = st.text_input("Equipo", key="eq1")
        lu = st.text_input("Lugar", key="l1")
        ce = st.text_input("Celador y DNI", key="c1")
        if st.form_submit_button("Registrar"):
            if all([en, eq, lu, ce]):
                if guardar_datos("RETIRADA", f, en, eq, lu, ce):
                    st.success("Guardado en Google Drive")

with t2:
    with st.form("f2", clear_on_submit=True):
        f2 = st.date_input("Fecha", key="d2")
        en2 = st.text_input("Enfermero y DNI", key="e2")
        eq2 = st.text_input("Equipo", key="eq2")
        lu2 = st.text_input("Lugar", key="l2")
        ce2 = st.text_input("Celador y DNI", key="c2")
        if st.form_submit_button("Registrar"):
            if all([en2, eq2, lu2, ce2]):
                if guardar_datos("ENTREGA", f2, en2, eq2, lu2, ce2):
                    st.success("Guardado en Google Drive")