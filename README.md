# Backend del Chatbot RAG con FastAPI -TEST KEVIN

Este proyecto contiene el backend para un chatbot inteligente, construido con FastAPI. Utiliza una arquitectura de **Retrieval-Augmented Generation (RAG)** para responder preguntas basándose en el contenido de un documento PDF, utilizando el modelo de lenguaje **Google Gemini**.

## Características

- **API Rápida**: Construido sobre FastAPI para un alto rendimiento.
- **Generación Aumentada por Recuperación (RAG)**: Proporciona respuestas contextualizadas y precisas basadas en un documento de conocimiento (`menu.pdf`).
- **Integración con Gemini**: Utiliza los modelos más recientes de Google para la generación de lenguaje natural.
- **Base de Datos Vectorial**: Almacena y busca eficientemente la información del documento usando ChromaDB.
- **Notificaciones Push**: Integrado con Firebase Admin SDK para enviar notificaciones a los dispositivos.
- **Documentación Automática**: Documentación interactiva de la API disponible en `/docs`.

## Instrucciones para Ejecutar el Proyecto

### Prerrequisitos

- Python 3.9 o superior.
- `pip` (gestor de paquetes de Python).

### 1. Configuración del Entorno

**a. Clona el repositorio y navega a la carpeta del backend:**
```bash
git clone <URL_DEL_REPOSITORIO>
cd chatbot_backend/backend
```

**b. Crea y activa un entorno virtual:**

- En Windows:
  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```
- En macOS/Linux:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

**c. Instala las dependencias:**
```bash
pip install -r requirements.txt
```

### 2. Configuración de Variables de Entorno

**a. Crea un archivo `.env`:**

Copia el archivo de ejemplo `.env.example` y renómbralo a `.env`.

**b. Añade tu API Key de Google:**

Abre el archivo `.env` y reemplaza `TU_API_KEY_DE_GOOGLE` con tu clave de API real de Google AI Studio.

```
GOOGLE_API_KEY="TU_API_KEY_DE_GOOGLE"
```

### 3. Configuración de Firebase (Opcional, para notificaciones)

Si deseas utilizar la funcionalidad de notificaciones push, necesitas una cuenta de servicio de Firebase.

1.  Ve a la consola de Firebase, a la configuración de tu proyecto -> Cuentas de servicio.
2.  Genera una nueva clave privada y descarga el archivo JSON.
3.  Renombra el archivo a `serviceAccountKey.json` y colócalo en la carpeta `backend/app/`.

### 4. Ejecutar el Servidor

Una vez que las dependencias y la configuración estén listas, inicia el servidor con Uvicorn:

```bash
uvicorn app.main:app --reload
```

- `--reload` hace que el servidor se reinicie automáticamente después de cambios en el código.

El servidor estará disponible en `http://127.0.0.1:8000`.

## Endpoints de la API

- **Documentación Interactiva**: `http://127.0.0.1:8000/docs`
- **Chat**: `POST /api/chat`
- **Registro de Dispositivos**: `POST /api/register-token`
- **Enviar Notificación**: `POST /api/send-notification`
- **Health Check**: `GET /health`
