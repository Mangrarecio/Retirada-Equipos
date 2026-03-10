import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import datetime
import textwrap
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión Retirada De Equipos", layout="centered")

# Estilos CSS para ocultar menús y forzar negritas
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
        
        # --- LIMPIEZA MATEMÁTICA Y RECONSTRUCCIÓN DE LA CLAVE ---
        clave_sucia = secrets_dict["private_key"]
        
        # 1. Quitamos los encabezados temporalmente
        clave_sucia = clave_sucia.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        
        # 2. Eliminamos CUALQUIER espacio, salto de línea (\n) o retorno de carro (\r)
        clave_sucia = re.sub(r'\s+', '', clave_sucia)
        
        # 3. Arreglamos el "Incorrect padding" añadiendo los "=" que falten para ser múltiplo de 4
        faltan = len(clave_sucia) % 4
        if faltan != 0:
            clave_sucia += '=' * (4 - faltan)
            
        # 4. Reconstruimos en los bloques exactos de 64 caracteres que exige Google
        clave_limpia = "\n".join(textwrap.wrap(clave_sucia, 64))
        clave_perfecta = f"-----BEGIN PRIVATE KEY-----\n{clave_limpia}\n-----END PRIVATE KEY-----\n"
        
        # Construimos el diccionario final
        info_servicio = {
            "type": secrets_dict.get("type", "service_account"),
            "project_id": secrets_dict["project_id"],
            "private_key_id": secrets_dict["private_key_id"],
            "private_key": clave_perfecta,
            "client_email": secrets_dict["client_email"],
            "client_id": secrets_dict["client_id"],
            "auth_uri": secrets_dict.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": secrets_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": secrets_dict.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": secrets_dict["client_x509_cert_url"],
        }
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credenciales = Credentials.from_service_account_info(info_servicio, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        
        return cliente.open("Retirada Equipos").sheet1
    
    except Exception as e:
        st.error(f"Error detallado de conexión: {e}")
        return None

def guardar_datos(tipo, fecha, enfermero_dni, equipo, lugar, celador_dni):
    hoja = conectar_google_sheets()
    if hoja:
        try:
            fila = [tipo, fecha.strftime("%d/%m/%Y"), enfermero_dni, equipo, lugar, celador_dni]
            hoja.append_row(fila)
            return True
        except Exception as e:
            st.error(f"Error al escribir en la hoja: {e}")
    return False

# --- PANTALLA DE ACCESO ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("Acceso al Sistema")
    password = st.text_input("Introduce la clave de seguridad", type="password")
    if st.button("Entrar"):
        if password == "@1357#":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# --- PANTALLA PRINCIPAL ---
st.title("Gestión Retirada De Equipos")
tab1, tab2 = st.tabs(["🔴 RETIRADA DE EQUIPO", "🟢 ENTREGA DE EQUIPO"])

# Formulario 1: Retirada
with tab1:
    with st.form("form_retirada", clear_on_submit=True):
        f_ret = st.date_input("Fecha de retirada")
        enf_ret = st.text_input("Nombre de enfermero y DNI")
        eq_ret = st.text_input("Equipo que se retira")
        lug_ret = st.text_input("Lugar de retirada")
        cel_ret = st.text_input("Nombre de celador y DNI")
        
        if st.form_submit_button("Registrar Movimiento"):
            if all([enf_ret, eq_ret, lug_ret, cel_ret]):
                if guardar_datos("RETIRADA", f_ret, enf_ret, eq_ret, lug_ret, cel_ret):
                    st.success("¡Movimiento registrado correctamente en la hoja de cálculo!")
            else:
                st.warning("Por favor, completa todos los campos")

# Formulario 2: Entrega
with tab2:
    with st.form("form_entrega", clear_on_submit=True):
        f_ent = st.date_input("Fecha de entrega")
        enf_ent = st.text_input("Nombre de enfermero y DNI")
        eq_ent = st.text_input("Equipo que se entrega")
        lug_ent = st.text_input("Lugar de entrega")
        cel_ent = st.text_input("Nombre de celador y DNI")
        
        if st.form_submit_button("Registrar Movimiento"):
            if all([enf_ent, eq_ent, lug_ent, cel_ent]):
                if guardar_datos("ENTREGA", f_ent, enf_ent, eq_ent, lug_ent, cel_ent):
                    st.success("¡Movimiento registrado correctamente en la hoja de cálculo!")
            else:
                st.warning("Por favor, completa todos los campos")