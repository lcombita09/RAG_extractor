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
    pdf_file_name = pathlib.Path(pdf_file_path).stem
    vectorstore_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', "vectorstores", pdf_file_name)
    if os.path.exists(vectorstore_path):
        vectorstore = FAISS.load_local(folder_path=vectorstore_path, embeddings=embeddings_model, allow_dangerous_deserialization=True)
    else:
        vectorstore = build_vectorstore(embeddings_model, pdf_file_name)
        vectorstore.save_local(vectorstore_path)
    return vectorstore

def extract_top_documents(vectorstore: FAISS, prompt_request, top_k, fetch_k):
    return [document.page_content for document in vectorstore.similarity_search(query=prompt_request, k=top_k, fetch_k=fetch_k)]

def parse_document(docs: List[Document]) -> str:
    '''
    Function to parse a list of documents into a string.
    '''
    return "\n".join([doc for doc in docs])

def load_retriever_queries():    
   # Load json with variables retrieval queries.
   
    with open("backend/variables_queries.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
        
    return json_data