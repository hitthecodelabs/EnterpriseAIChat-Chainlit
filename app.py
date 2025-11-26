import chainlit as cl
import httpx  # Reemplaza a 'requests' para soporte asíncrono real
import os
import logging
import asyncio
from typing import List, Dict

# --- 1. CONFIGURACIÓN Y LOGGING ---
# Configuración del Logger para entornos corporativos
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Config:
    """Centralización de variables de entorno y constantes."""
    API_URL = os.getenv("BACKEND_API_URL")
    API_SECRET = os.getenv("BACKEND_API_SECRET")
    
    # Configuración de Personalidad (Fácilmente ajustable para otros proyectos)
    BOT_NAME = os.getenv("BOT_NAME", "Maria")
    BOT_ROLE = os.getenv("BOT_ROLE", "Specialist Agent")
    WELCOME_MSG = f"👋 **Hello! I'm {BOT_NAME}**\n\nI'm your {BOT_ROLE}. I can check orders, help with returns, or answer product questions."
    
    # UX Timing
    TIMEOUT_SECONDS = 45
    TRANSITION_DELAY = 2.0  # Reducido a 2s para mejor UX

# --- 2. GESTIÓN DEL ESTADO (MEMORIA) ---
def get_history() -> List[Dict]:
    """Recupera el historial de la sesión actual."""
    return cl.user_session.get("history", [])

def update_history(role: str, content: str):
    """Agrega un mensaje al historial de la sesión."""
    history = get_history()
    history.append({"role": role, "content": content})
    cl.user_session.set("history", history)

# --- 3. CICLO DE VIDA DEL CHAT ---
@cl.on_chat_start
async def start():
    """Inicialización de la sesión."""
    # Validación de Seguridad
    if not Config.API_URL or not Config.API_SECRET:
        logger.error("Faltan variables de entorno críticas (API_URL o API_SECRET).")
        await cl.Message(content="⚠️ **System Error:** Configuration missing. Please contact support.").send()
        return

    # Inicializar historial vacío para esta sesión
    cl.user_session.set("history", [])

    await cl.Message(content=Config.WELCOME_MSG).send()

@cl.on_message
async def main(message: cl.Message):
    """Manejo principal del flujo de mensajes."""
    
    # A. Actualizar memoria con el mensaje del usuario
    update_history("user", message.content)
    current_history = get_history()

    # B. Feedback Visual Inicial
    status_msg = cl.Message(content="🧠 *Thinking...*")
    await status_msg.send()

    # C. Preparar Payload
    payload = {
        "message": message.content,
        "history": current_history 
    }
    
    headers = {
        "x-secret": Config.API_SECRET,
        "Content-Type": "application/json"
    }

    # D. Comunicación Asíncrona con el Backend (Middleware)
    ai_response = ""
    try:
        async with httpx.AsyncClient(timeout=Config.TIMEOUT_SECONDS) as client:
            response = await client.post(Config.API_URL, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get("response", "")
                category = data.get("category", "General")
                
                # --- UX: TRANSICIÓN DE AGENTE ---
                if category != "AccountProfileOther" and category != "General":
                    status_msg.content = f"🔄 *Connecting you to the {category} Specialist...*"
                    await status_msg.update()
                    # Pausa controlada para efecto psicológico
                    await asyncio.sleep(Config.TRANSITION_DELAY)
                else:
                    # Limpieza visual si no hay cambio de contexto
                    await status_msg.remove()

                # E. Enviar respuesta final
                await cl.Message(content=ai_response).send()
                
                # F. Guardar respuesta de la IA en memoria
                update_history("assistant", ai_response)

            else:
                error_msg = f"Server returned status {response.status_code}"
                logger.error(error_msg)
                status_msg.content = f"⚠️ **Service Unavailable:** We are experiencing high traffic."
                await status_msg.update()

    except httpx.TimeoutException:
        logger.error("Timeout esperando respuesta del Middleware.")
        status_msg.content = "⚠️ **Timeout:** The specialist is taking too long to respond. Please try again."
        await status_msg.update()
        
    except Exception as e:
        logger.error(f"Error de conexión no controlado: {str(e)}")
        status_msg.content = "⚠️ **Connection Error:** Could not reach the intelligent services."
        await status_msg.update()