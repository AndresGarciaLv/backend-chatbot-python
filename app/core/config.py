"""
Módulo de Configuración Global.

Este módulo utiliza Pydantic Settings para gestionar la configuración de la aplicación,
cargando variables de entorno desde un archivo .env. Esto centraliza la configuración
y facilita la gestión de diferentes entornos (desarrollo, producción, etc.).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    """
    Clase de configuración que carga variables de entorno.

    Define los parámetros de configuración de la aplicación y los carga desde
    el entorno. Utiliza SettingsConfigDict para especificar que el archivo
    de donde se cargan las variables es `.env`.
    """
    # Configuración para cargar desde el archivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    # Variables de entorno
    GOOGLE_API_KEY: str
    CHROMA_PERSIST_DIR: str
    MODEL_NAME: str
    EMBEDDING_MODEL_NAME: str

@lru_cache
def get_settings() -> Settings:
    """
    Retorna una instancia única de la configuración.

    Utiliza lru_cache para asegurar que la clase Settings se instancie una sola vez
    (patrón Singleton), mejorando la eficiencia al evitar lecturas repetidas del
    archivo .env.

    Returns:
        Settings: Una instancia de la clase de configuración.
    """
    return Settings()
