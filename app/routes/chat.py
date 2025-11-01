"""
Módulo de Rutas de la API para el Chatbot.

Este módulo define los endpoints de la API relacionados con la funcionalidad del chatbot.
Incluye el endpoint principal `/chat` para interactuar con el modelo RAG y un
endpoint adicional `/upload-pdf` para actualizar la base de conocimiento.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, status
from pydantic import BaseModel

from app.core.rag_chain import get_rag_chain
from app.services.pdf_service import process_and_update_vector_store

# Crear un router para agrupar los endpoints del chat
router = APIRouter()

# --- Modelos de Datos (Pydantic) ---

class ChatRequest(BaseModel):
    """Modelo para la petición del endpoint /chat."""
    question: str

class ChatResponse(BaseModel):
    """Modelo para la respuesta del endpoint /chat."""
    answer: str

# --- Endpoints de la API ---

@router.post("/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest):
    """
    Endpoint para recibir preguntas y devolver respuestas del chatbot RAG.

    Utiliza la cadena RAG pre-inicializada para procesar la pregunta del usuario
    y generar una respuesta basada en el contexto de la base de datos vectorial.

    Args:
        request (ChatRequest): La petición con la pregunta del usuario.

    Returns:
        ChatResponse: La respuesta generada por el modelo.
    """
    try:
        rag_chain = get_rag_chain()
        answer = rag_chain.invoke(request.question)
        return ChatResponse(answer=answer)
    except Exception as e:
        # Manejo de errores genérico
        print(f"Error en el endpoint /chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al procesar la pregunta: {str(e)}"
        )

@router.post("/upload-pdf", summary="Subir un nuevo PDF para actualizar el contexto")
def upload_pdf(file: UploadFile = File(...)):
    """
    Endpoint para subir un archivo PDF y actualizar la base de datos vectorial.

    Valida que el archivo sea un PDF y luego llama al servicio correspondiente
    para procesarlo y actualizar el almacén de vectores.

    Args:
        file (UploadFile): El archivo PDF enviado como multipart/form-data.

    Returns:
        dict: Un mensaje de confirmación.
    """
    if file.content_type != 'application/pdf':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de archivo no válido. Por favor, sube un PDF."
        )
    
    try:
        process_and_update_vector_store(file)
        return {"message": "Nuevo PDF procesado y base de datos vectorial actualizada exitosamente."}
    except Exception as e:
        print(f"Error en el endpoint /upload-pdf: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al procesar el archivo PDF: {str(e)}"
        )
