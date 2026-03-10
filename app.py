import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import re
import base64

def conectar_google_sheets():
    try:
        s = st.secrets["gcp_service_account"]
        
        # 1. Extraemos la clave cruda
        pk = s["private_key"]
        
        # 2. Limpieza profunda: quitamos cabeceras, saltos de línea y espacios
        pk_body = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        pk_body = re.sub(r'\s+', '', pk_body) # Elimina CUALQUIER espacio o salto invisible
        
        # 3. CORRECCIÓN DE PADDING (El error que te da)
        # Añadimos los '=' necesarios para que la longitud sea múltiplo de 4
        missing_padding = len(pk_body) % 4
        if missing_padding:
            pk_body += '=' * (4 - missing_padding)
        
        # 4. Reconstrucción estándar
        pk_final = f"-----BEGIN PRIVATE KEY-----\n{pk_body}\n-----END PRIVATE KEY-----\n"
        
        info_servicio = {
            "type": s.get("type", "service_account"),
            "project_id": s["project_id"],
            "private_key_id": s["private_key_id"],
            "private_key": pk_final,
            "client_email": s["client_email"],
            "client_id": s["client_id"],
            "auth_uri": s.get("auth_uri", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": s.get("token_uri", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": s.get("auth_provider_x509_cert_url", "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": s["client_x509_cert_url"],
        }
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        credenciales = Credentials.from_service_account_info(info_servicio, scopes=scopes)
        cliente = gspread.authorize(credenciales)
        
        # IMPORTANTE: Asegúrate de que el nombre sea el de la hoja actual
        return cliente.open("Retirada Equipos").sheet1
        
    except Exception as e:
        st.error(f"Error crítico de conexión: {e}")
        return None