import os
from typing import List
from utils import load_secrets, get_embeddings_model
from retriever import load_vectorstore, extract_top_documents, parse_document
from augmented_generator import llm_response
from prompt_engineering import GET_CONTEXT_PROMPT_SYSTEM, GET_CONTEXT_PROMPT_USER, CHATBOT_PROMPT_SYSTEM, CHATBOT_PROMPT_USER

def chatbot_response(vectorstore_name: str, input_text: str, chat_history: List[str]):
    """
    Genera una respuesta del chatbot basada en el contexto del documento y el historial de chat.

    Esta función principal coordina el proceso de generación de respuestas, incluyendo la carga
    de documentos, reformulación de preguntas y generación de respuestas contextuales.

    Args:
        vectorstore_name (str): Nombre del archivo del vectorstore (sin extensión .pdf)
        input_text (str): Texto de entrada o pregunta del usuario
        chat_history (List[str]): Historial de conversaciones previas

    Returns:
        dict: Respuesta del modelo LLM en formato streaming

    Note:
        Requiere variables de entorno:
        - DOCUMENTS_TO_RETRIEVE: Número de documentos a recuperar
        - DOCUMENTS_TO_FETCH: Número de documentos a filtrar
    """
    load_secrets([".env.file", ".env.secrets"])

    vectorstore = load_vectorstore(embeddings_model=get_embeddings_model(),
                                 pdf_file_path=f"{vectorstore_name}.pdf")

    user_question = reformulate_user_question(input_text, chat_history)

    fetch_k = int(os.getenv("DOCUMENTS_TO_RETRIEVE"))
    top_k = int(os.getenv("DOCUMENTS_TO_FETCH"))

    return generate_chatbot_response(user_question, vectorstore, top_k, fetch_k)

def reformulate_user_question(input_text: str, chat_history: List[str]) -> str:
    """
    Reformula la pregunta del usuario considerando el contexto del historial de chat.

    Esta función utiliza el historial de conversación para generar una pregunta más
    contextualizada y relevante.

    Args:
        input_text (str): Pregunta original del usuario
        chat_history (List[str]): Historial de conversaciones previas

    Returns:
        str: Pregunta reformulada considerando el contexto histórico

    Note:
        - Si no hay historial, retorna la pregunta original
        - Considera hasta las últimas 5 preguntas del historial
    """
    if len(chat_history) == 0:
        return input_text

    user_questions = chat_history[::2]
    if len(user_questions) > 5:
        user_questions = user_questions[-5:]
    else:
        user_questions = chat_history

    prompt_user = GET_CONTEXT_PROMPT_USER.format(
        question=input_text,
        history_questions=user_questions
    )
    llm_answer = llm_response(
        prompt_system=GET_CONTEXT_PROMPT_SYSTEM,
        prompt_user=prompt_user
    ).choices[0].message.content

    return llm_answer

def generate_chatbot_response(user_question: str, vectorstore, top_k: int, fetch_k: int):
    """
    Genera una respuesta del chatbot basada en documentos relevantes y la pregunta del usuario.

    Esta función recupera documentos relevantes del vectorstore y genera una respuesta
    contextualizada utilizando un modelo LLM.

    Args:
        user_question (str): Pregunta reformulada del usuario
        vectorstore: Instancia del almacén de vectores FAISS
        top_k (int): Número de documentos a retornar
        fetch_k (int): Número de documentos a recuperar antes de filtrar

    Returns:
        dict: Respuesta del modelo LLM en formato streaming
    """
    top_documents = extract_top_documents(
        vectorstore,
        prompt_request=user_question,
        top_k=top_k,
        fetch_k=fetch_k
    )
    llm_context = parse_document(top_documents)

    prompt_user = CHATBOT_PROMPT_USER.format(
        question=user_question,
        context=llm_context
    )
    return llm_response(
        prompt_system=CHATBOT_PROMPT_SYSTEM,
        prompt_user=prompt_user,
        stream=True
    )
