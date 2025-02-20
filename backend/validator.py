import os
from utils import load_secrets, get_embeddings_model
from retriever import load_vectorstore, extract_top_documents, parse_document
from augmented_generator import llm_response
from prompt_engineering import CHATBOT_PROMPT_SYSTEM, CHATBOT_PROMPT_USER

def validator_response(vectorstore_name: str, input_prompt: str, input_llm: str) -> str:
    """
    Genera una respuesta validada utilizando un sistema RAG (Retrieval-Augmented Generation).

    Esta función coordina el proceso de validación de respuestas, incluyendo la carga
    de documentos relevantes y la generación de respuestas basadas en contexto.

    Args:
        vectorstore_name (str): Nombre del archivo del vectorstore (sin extensión .pdf)
        input_prompt (str): Prompt inicial para la búsqueda de contexto relevante
        input_llm (str): Prompt para generar la respuesta final

    Returns:
        str: Respuesta generada y validada por el modelo

    Note:
        Requiere las siguientes variables de entorno:
        - DOCUMENTS_TO_RETRIEVE: Número de documentos a recuperar
        - DOCUMENTS_TO_FETCH: Número de documentos a filtrar

    Example:
        response = validator_response(
            "knowledge_base",
            "¿Qué es machine learning?",
            "Explica el concepto de machine learning"
        )
    """
    load_secrets([".env.file", ".env.secrets"])

    vectorstore = load_vectorstore(
        embeddings_model=get_embeddings_model(),
        pdf_file_path=f"{vectorstore_name}.pdf"
    )

    fetch_k = int(os.getenv("DOCUMENTS_TO_RETRIEVE"))
    top_k = int(os.getenv("DOCUMENTS_TO_FETCH"))

    return generate_validator_response(
        vectorstore,
        input_prompt,
        input_llm,
        top_k,
        fetch_k
    )

def generate_validator_response(vectorstore, input_prompt: str, input_llm: str,
                              top_k: int, fetch_k: int) -> str:
    """
    Genera una respuesta validada basada en documentos relevantes y prompts específicos.

    Esta función recupera documentos relevantes del vectorstore y genera una respuesta
    contextualizada utilizando un modelo LLM.

    Args:
        vectorstore: Instancia del almacén de vectores FAISS
        input_prompt (str): Prompt para buscar documentos relevantes
        input_llm (str): Prompt para generar la respuesta final
        top_k (int): Número de documentos a retornar
        fetch_k (int): Número de documentos a recuperar antes de filtrar

    Returns:
        str: Contenido de la respuesta generada por el modelo

    Note:
        Utiliza los prompts definidos en CHATBOT_PROMPT_SYSTEM y CHATBOT_PROMPT_USER
        para generar respuestas contextualizadas.
    """
    top_documents = extract_top_documents(
        vectorstore,
        prompt_request=input_prompt,
        top_k=top_k,
        fetch_k=fetch_k
    )
    llm_context = parse_document(top_documents)

    prompt_user = CHATBOT_PROMPT_USER.format(
        question=input_llm,
        context=llm_context
    )
    return llm_response(
        prompt_system=CHATBOT_PROMPT_SYSTEM,
        prompt_user=prompt_user
    ).choices[0].message.content