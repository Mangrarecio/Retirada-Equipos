import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import re

# --- CONFIGURACIÓN DE PÁGINA E INTERFAZ LIMPIA ---
st.set_page_config(page_title="Gestión Retirada De Equipos", layout="centered")

# CSS para ocultar TODO: Barra superior, menú de la derecha (Deploy) y pie de página
st.markdown("""
    <style>
    /* Ocultar barra superior y botón de Deploy */
    header {visibility: hidden !important;}
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    .stAppDeployButton {display:none !important;}
    
    /* Forzar negritas en los textos para mejor visibilidad */
    p, label, .stMarkdown, .stButton {
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONEXIÓN SEGURA A GOOGLE SHEETS ---
def conectar_google_sheets():
    try:
        s = st.secrets["gcp_service_account"]
        
        # Limpieza de la clave privada para evitar errores de padding/formato
        pk = s["private_key"]
        # Extraer solo el contenido base64 y limpiar caracteres basura
        contenido = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        contenido_limpio = re.sub(r'[^A-Za-z0-9+/=]', '', contenido)
        
        # Corregir padding si faltan signos '='
        faltan = len(contenido_limpio) % 4
        if faltan:
            contenido_limpio += '=' * (4 - faltan)
            
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
        
        # Nombre de la hoja en Drive
        return cliente.open("Retirada Equipos").sheet1
    except Exception as e:
        st.error(f"Error de conexión: Verifica que hayas compartido la hoja con el email de la cuenta de servicio.")
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

# --- CONTROL DE ACCESO ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("Acceso al Sistema")
    pwd = st.text_input("Introduce la clave", type="password")
    if st.button("Entrar"):
        if pwd == "@1357#":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    st.stop()

# --- APLICACIÓN PRINCIPAL ---
st.title("Gestión Retirada De Equipos")

t1, t2 = st.tabs(["🔴 RETIRADA DE EQUIPO", "🟢 ENTREGA DE EQUIPO"])

with t1:
    with st.form("form_ret", clear_on_submit=True):
        f = st.date_input("Fecha de retirada")
        en = st.text_input("Enfermero y DNI")
        eq = st.text_input("Equipo")
        lu = st.text_input("Lugar")
        ce = st.text_input("Celador y DNI")
        if st.form_submit_button("Registrar Movimiento"):
            if all([en, eq, lu, ce]):
                if guardar_datos("RETIRADA", f, en, eq, lu, ce):
                    st.success("✅ Datos guardados en Google Drive")
            else:
                st.warning("Completa todos los campos")

with t2:
    with st.form("form_ent", clear_on_submit=True):
        f2 = st.date_input("Fecha de entrega")
        en2 = st.text_input("Enfermero y DNI")
        eq2 = st.text_input("Equipo")
        lu2 = st.text_input("Lugar")
        ce2 = st.text_input("Celador y DNI")
        if st.form_submit_button("Registrar Movimiento"):
            if all([en2, eq2, lu2, ce2]):
                if guardar_datos("ENTREGA", f2, en2, eq2, lu2, ce2):
                    st.success("✅ Datos guardados en Google Drive")
            else:
                st.warning("Completa todos los campos")