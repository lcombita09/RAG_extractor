import json
import pathlib
import os
from typing import List

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.faiss import FAISS


# Build Vector Store.
def build_vectorstore(embeddings_model, pdf_file_name):
    """
    Construye un vectorstore a partir de un archivo PDF.

    Esta función carga un PDF, lo divide en fragmentos más pequeños y crea un índice
    FAISS con los embeddings de estos fragmentos.

    Args:
        embeddings_model: Modelo de embeddings a utilizar
        pdf_file_name (str): Nombre del archivo PDF sin la extensión

    Returns:
        FAISS: Instancia del vector store FAISS construido

    Note:
        El PDF debe estar ubicado en el directorio 'pdf_files'
    """
    
    # Load pdf as langchain document object
    pdf_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', "pdf_files", f'{pdf_file_name}.pdf')
    loader = PyMuPDFLoader(pdf_file_path)
    main_documents = loader.load()  

    document_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4500,
            chunk_overlap=1000,
            length_function=len,
            is_separator_regex=False,
        )

    splitted_documents = document_splitter.split_documents(main_documents)
    
    return FAISS.from_documents(documents=splitted_documents, embedding=embeddings_model)
    
def load_vectorstore(embeddings_model, pdf_file_path):
    """
    Carga o crea un vector store FAISS para un archivo PDF.

    Si existe un vector store previamente guardado, lo carga.
    Si no existe, lo crea y lo guarda para uso futuro.

    Args:
        embeddings_model: Modelo de embeddings a utilizar
        pdf_file_path (str): Ruta completa al archivo PDF

    Returns:
        FAISS: Instancia del vector store FAISS

    Note:
        Los vectorstores se guardan en el directorio 'vectorstores'
    """
    
    pdf_file_name = pathlib.Path(pdf_file_path).stem
    vectorstore_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', "vectorstores", pdf_file_name)
    if os.path.exists(vectorstore_path):
        vectorstore = FAISS.load_local(folder_path=vectorstore_path, embeddings=embeddings_model, allow_dangerous_deserialization=True)
    else:
        vectorstore = build_vectorstore(embeddings_model, pdf_file_name)
        vectorstore.save_local(vectorstore_path)
    return vectorstore

def extract_top_documents(vectorstore: FAISS, prompt_request, top_k, fetch_k):
    """
    Extrae los documentos más similares a una consulta del vector store 

    Args:
        vectorstore (FAISS): vector store FAISS
        prompt_request (str): Consulta para buscar documentos similares
        top_k (int): Número de documentos a retornar
        fetch_k (int): Número de documentos a recuperar antes de filtrar

    Returns:
        List[str]: Lista de contenidos de los documentos más similares
    """
    return [document.page_content for document in vectorstore.similarity_search(query=prompt_request, k=top_k, fetch_k=fetch_k)]

def parse_document(docs: List[Document]) -> str:
    """
    Combina una lista de documentos en una única cadena de texto.

    Args:
        docs (List[Document]): Lista de documentos a combinar

    Returns:
        str: Cadena de texto combinada con los contenidos de los documentos
    """
    return "\n".join([doc for doc in docs])

def load_retriever_queries():    
    """
    Carga las consultas a pasar al retriever desde un archivo JSON.

    Returns:
        dict: Diccionario con las consultas de recuperación

    Note:
        El archivo JSON está ubicado en 'backend/variables_queries.json'
    """
   
    with open("backend/variables_queries.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
        
    return json_data