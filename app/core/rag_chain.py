"""
Módulo de la Cadena RAG (Retrieval-Augmented Generation).

Este módulo define la lógica principal del sistema RAG. Construye y expone
una cadena de LangChain que integra un retriever, un prompt, el modelo de lenguaje
y un parser de salida para generar respuestas basadas en contexto.
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.core.vector_store import vector_store_instance

# Obtener la configuración de la aplicación
settings = get_settings()

# --- 1. Definir el Retriever ---
# El retriever se obtiene del vector store inicializado.
# `search_kwargs={'k': 3}` indica que se recuperarán los 3 chunks más relevantes.
retriever = vector_store_instance.as_retriever(search_kwargs={'k': 3})

# --- 2. Definir el Prompt Template ---
# Este template estructura la pregunta que se le hará al LLM.
# Incluye el contexto recuperado y la pregunta del usuario.
prompt_template = """
Eres un asistente de inteligencia artificial amigable y servicial, especializado en responder 
preguntas sobre el menú de un restaurante. Tu objetivo es proporcionar respuestas claras, 
concisas y precisas, basándote únicamente en el contexto que se te proporciona a continuación.

Si la información para responder la pregunta no se encuentra en el contexto, debes indicar 
respetuosamente que no tienes la información solicitada. No intentes inventar una respuesta.

Contexto:
{context}

Pregunta:
{question}

Respuesta:
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# --- 3. Inicializar el Modelo de Lenguaje (LLM) ---
# Se utiliza el modelo Gemini especificado en la configuración.
llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.3  # Un valor bajo para respuestas más predecibles y consistentes
)

# --- 4. Definir el Parser de Salida ---
# Convierte la salida del LLM (un objeto de mensaje) a una cadena de texto simple.
output_parser = StrOutputParser()

# --- 5. Construir la Cadena RAG (LCEL) ---
# Se utiliza LangChain Expression Language (LCEL) para encadenar los componentes.
# El flujo es el siguiente:
# 1. `RunnablePassthrough`: Pasa la pregunta del usuario al retriever y al prompt.
# 2. `retriever`: Obtiene los documentos relevantes de ChromaDB.
# 3. `prompt`: Formatea el prompt con el contexto y la pregunta.
# 4. `llm`: Genera una respuesta basada en el prompt formateado.
# 5. `output_parser`: Extrae el texto de la respuesta del LLM.
rag_chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | output_parser
)

def get_rag_chain():
    """
    Retorna la cadena RAG pre-construida.

    Esta función permite acceder a la cadena RAG inicializada desde otros
    módulos de la aplicación, asegurando que se use la misma instancia.

    Returns:
        Runnable: La cadena de LangChain lista para ser invocada.
    """
    return rag_chain
