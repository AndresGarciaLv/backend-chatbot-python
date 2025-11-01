"""
Módulo de Servicio para PDF.

Este módulo contiene la lógica de negocio para procesar archivos PDF.
Se encarga de cargar el contenido de un PDF, dividirlo en fragmentos (chunks)
y actualizar la base de datos vectorial con los nuevos documentos.
"""

import os
import tempfile
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.vector_store import vector_store_instance, embeddings

def process_and_update_vector_store(file: UploadFile):
    """
    Procesa un archivo PDF y actualiza la base de datos vectorial.

    Guarda el archivo PDF subido en un directorio temporal, lo carga usando
    PyPDFLoader, lo divide en chunks de texto y finalmente añade estos chunks
    a la instancia de ChromaDB, actualizando así el contexto para el RAG.

    Args:
        file (UploadFile): El archivo PDF subido a través de la API.

    Raises:
        Exception: Si ocurre un error durante el procesamiento del archivo.
    """
    try:
        # Crear un archivo temporal para guardar el PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(file.file.read())
            tmp_file_path = tmp_file.name

        print(f"Archivo PDF temporal guardado en: {tmp_file_path}")

        # 1. Cargar el PDF
        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()

        # 2. Dividir el documento en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Tamaño de cada chunk en caracteres
            chunk_overlap=100   # Superposición entre chunks para mantener contexto
        )
        chunks = text_splitter.split_documents(documents)

        print(f"PDF dividido en {len(chunks)} chunks.")

        # 3. Añadir los chunks a la base de datos vectorial
        vector_store_instance.add_documents(chunks)
        print("Base de datos vectorial actualizada con los nuevos chunks.")

    except Exception as e:
        print(f"Error procesando el archivo PDF: {e}")
        # Re-lanzar la excepción para que sea manejada en la capa de la API
        raise e
    finally:
        # Eliminar el archivo temporal después del procesamiento
        if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)
            print(f"Archivo temporal eliminado: {tmp_file_path}")


def process_pdf_from_path(file_path: str):
    """
    Procesa un archivo PDF desde una ruta local y actualiza la base de datos vectorial.

    Args:
        file_path (str): La ruta al archivo PDF.

    Raises:
        Exception: Si ocurre un error durante el procesamiento del archivo.
    """
    try:
        print(f"Cargando archivo PDF desde: {file_path}")

        # 1. Cargar el PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # 2. Dividir el documento en chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Tamaño de cada chunk en caracteres
            chunk_overlap=100   # Superposición entre chunks para mantener contexto
        )
        chunks = text_splitter.split_documents(documents)

        print(f"PDF dividido en {len(chunks)} chunks.")

        # 3. Añadir los chunks a la base de datos vectorial
        vector_store_instance.add_documents(chunks)
        print("Base de datos vectorial actualizada con los nuevos chunks.")

    except Exception as e:
        print(f"Error procesando el archivo PDF desde la ruta: {e}")
        # Re-lanzar la excepción para que sea manejada en un nivel superior si es necesario
        raise e