"""
Módulo Principal de la Aplicación FastAPI.

Este archivo es el punto de entrada de la aplicación. Aquí se crea la instancia
de FastAPI, se configura el middleware (como CORS), se incluyen los routers
de los diferentes módulos y se definen endpoints globales como el de health check.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import firebase_admin
from firebase_admin import credentials, messaging
from pydantic import BaseModel

# Importar la configuración y los routers
from app.core.config import get_settings
from app.routes import chat
from app.services.pdf_service import process_pdf_from_path

# Cargar las variables de entorno al inicio
# Esto es importante para que google.generativeai configure su API KEY
from dotenv import load_dotenv
load_dotenv()

# Es crucial que la API key de Google se configure antes de importar otros módulos
# que puedan usarla, como rag_chain o vector_store.
import google.generativeai as genai
settings = get_settings()
try:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
except Exception as e:
    print(f"Error al configurar la API de Google: {e}")
    print("Asegúrate de que la variable de entorno GOOGLE_API_KEY está configurada correctamente.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Código que se ejecuta al inicio de la aplicación
    print("Iniciando la aplicación...")

    # Inicializar Firebase Admin
    try:
        cred = credentials.Certificate("app/serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK inicializado correctamente.")
    except Exception as e:
        print(f"Error al inicializar Firebase Admin SDK: {e}")

    pdf_path = "app/data/menu.pdf"
    if os.path.exists(pdf_path):
        print(f"Procesando el archivo PDF: {pdf_path}")
        try:
            process_pdf_from_path(pdf_path)
            print("PDF procesado y cargado en la base de datos vectorial.")
        except Exception as e:
            print(f"Error al procesar el PDF durante el inicio: {e}")
    else:
        print(f"Advertencia: No se encontró el archivo PDF en {pdf_path}. El chatbot podría no tener contexto.")
    yield
    # Código que se ejecuta al final de la aplicación (limpieza)
    print("La aplicación se está cerrando...")

# Crear la instancia de la aplicación FastAPI
app = FastAPI(
    title="Chatbot RAG con FastAPI y Gemini",
    description="Un backend para un chatbot con RAG, usando FastAPI, LangChain y Google Gemini.",
    version="1.0.0",
    lifespan=lifespan
)

# --- Modelos de Pydantic ---
class NotificationRequest(BaseModel):
    title: str
    body: str

class FcmTokenRequest(BaseModel):
    token: str

# --- Almacenamiento en memoria para tokens FCM ---
# En una aplicación real, esto debería ser una base de datos (ej. Redis, PostgreSQL).
fcm_tokens = set()


# --- Configuración de Middleware ---

# Configurar CORS (Cross-Origin Resource Sharing)
# Esto permite que el frontend (ej. una app Flutter) se comunique con el backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todas las origenes (en producción, sé más restrictivo)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todas las cabeceras
)

# --- Inclusión de Routers ---

# Incluir el router del chat para que sus endpoints estén disponibles
app.include_router(chat.router, prefix="/api", tags=["Chatbot"])


# --- Endpoints Globales ---

@app.get("/", include_in_schema=False)
def root():
    """Redirige la ruta raíz a la documentación de la API."""
    return RedirectResponse(url="/docs")

@app.get("/health", summary="Verificar estado del servidor", tags=["Health Check"])
def health_check():
    """
    Endpoint de Health Check.
    
    Retorna un estado simple para confirmar que el servidor está en funcionamiento.
    """
    return {"status": "ok", "message": "Servidor funcionando correctamente."}

@app.post("/api/register-token", summary="Registrar token FCM", tags=["Notifications"])
async def register_fcm_token(request: FcmTokenRequest):
    """
    Registra un token FCM de un dispositivo para futuras notificaciones.
    """
    if request.token not in fcm_tokens:
        fcm_tokens.add(request.token)
        print(f"Token FCM registrado: {request.token}")
        print(f"Tokens actuales: {list(fcm_tokens)}")
    return {"message": "Token FCM registrado con éxito"}

@app.post("/api/send-notification", summary="Enviar notificación a todos los dispositivos", tags=["Notifications"])
async def send_notification_to_all(request: NotificationRequest):
    """
    Envía una notificación push a todos los dispositivos registrados a través de FCM.
    """
    if not fcm_tokens:
        raise HTTPException(status_code=404, detail="No hay tokens FCM registrados.")

    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=request.title,
            body=request.body,
        ),
        tokens=list(fcm_tokens),
    )

    try:
        response = messaging.send_multicast(message)
        print(f"Notificaciones enviadas. Éxitos: {response.success_count}, Fallos: {response.failure_count}")
        if response.failure_count > 0:
            # Opcional: registrar los tokens que fallaron para futura limpieza
            failed_tokens = []
            for i, resp in enumerate(response.responses):
                if not resp.success:
                    failed_tokens.append(list(fcm_tokens)[i])
            print(f"Tokens con error: {failed_tokens}")
        return {"message": f"Notificaciones enviadas. Éxitos: {response.success_count}, Fallos: {response.failure_count}"}
    except Exception as e:
        print(f"Error al enviar las notificaciones: {e}")
        raise HTTPException(status_code=500, detail=f"Error al enviar las notificaciones: {e}")
