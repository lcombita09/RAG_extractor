import os
from dotenv import load_dotenv
from typing import List, Union
import pathlib
from langchain_openai import AzureOpenAIEmbeddings, OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document

def load_secrets(secrets_files: List) -> None:
    """
    Carga las variables de entorno desde los archivos especificados.    

    Args:
        secrets_files (List): Lista de rutas a los archivos de secretos (.env)

    Returns:
        None

    Example:
        load_secrets(['secrets.env'])
    """
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    for secrets_file in secrets_files:
        secrets_file_path = os.path.join(parent_dir, '..', secrets_file)
        load_dotenv(secrets_file_path)

def get_embeddings_model() -> Union[AzureOpenAIEmbeddings, OpenAIEmbeddings]:
    """
    Inicializa y retorna un modelo de embeddings basado en la configuración del entorno.

    Esta función determina qué tipo de modelo de embeddings usar (Azure OpenAI o OpenAI)
    basándose en la variable de entorno LLM_MODEL. Configura las credenciales necesarias
    y retorna el modelo de embeddings correspondiente.

    Returns:
        Union[AzureOpenAIEmbeddings, OpenAIEmbeddings]: Instancia del modelo de embeddings configurado

    Raises:
        EnvironmentError: Si las variables de entorno requeridas no están configuradas

    Note:
        Requiere que las siguientes variables de entorno estén configuradas:
        - LLM_MODEL: Tipo de modelo a usar ('azure' u 'openai')
        - Para Azure: AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, LLM_EMBEDDING_MODEL
        - Para OpenAI: OPENAI_API_KEY
    """
    if "azure" in os.getenv("LLM_MODEL").lower():
        os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
        os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
        cloud_embeddings = AzureOpenAIEmbeddings(
            model=os.getenv("LLM_EMBEDDING_MODEL"),
        )
    elif "openai" in os.getenv("LLM_MODEL").lower():
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        cloud_embeddings = OpenAIEmbeddings()
    return cloud_embeddings