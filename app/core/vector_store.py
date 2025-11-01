"""
Módulo de Almacén de Vectores.

Este módulo se encarga de la inicialización y gestión de la base de datos vectorial
ChromaDB. Proporciona una función para obtener o crear una instancia de la base de
datos de forma persistente.
"""

import os
import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

from app.core.config import get_settings

# Obtener la configuración de la aplicación
settings = get_settings()

# Inicializar el modelo de embeddings una sola vez
embeddings = GoogleGenerativeAIEmbeddings(
    model=settings.EMBEDDING_MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY
)

def get_vector_store() -> Chroma:
    """
    Obtiene o crea la base de datos vectorial ChromaDB.

    Verifica si el directorio de persistencia de ChromaDB existe. Si existe, carga
    la base de datos. Si no, la crea, añade un documento inicial para evitar errores
    y la persiste en el disco.

    Returns:
        Chroma: Una instancia de la base de datos vectorial Chroma.
    """
    persist_directory = settings.CHROMA_PERSIST_DIR

    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        print(f"Cargando ChromaDB existente desde: {persist_directory}")
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        print(f"Creando nueva ChromaDB en: {persist_directory}")
        os.makedirs(persist_directory, exist_ok=True)
        # Crear una colección con un documento inicial para evitar errores
        vector_store = Chroma.from_texts(
            texts=["Este es un documento inicial para la base de datos vectorial."],
            embedding=embeddings,
            persist_directory=persist_directory
        )
    return vector_store

# Inicializar el vector store al arrancar para que esté disponible globalmente
vector_store_instance = get_vector_store()
