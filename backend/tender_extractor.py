import os
import json
import re
import pandas as pd
from ragas import SingleTurnSample
from augmented_generator import llm_response
from evaluation_pipeline import rag_system_evaluation, load_ground_truth
from utils import load_secrets, get_embeddings_model
from prompt_engineering import SUMMARIZER_PROMPT_SYSTEM, SUMMARIZER_PROMPT_USER
from retriever import load_vectorstore, extract_top_documents, parse_document, load_retriever_queries

def tender_data_extractor(pdf_file_path: str) -> dict:
    """
    Extrae información estructurada de un documento de licitación en PDF.

    Esta función coordina el proceso de extracción de información utilizando un sistema RAG,
    procesando múltiples variables definidas y generando un resumen estructurado.

    Args:
        pdf_file_path (str): Ruta al archivo PDF de la licitación

    Returns:
        dict: Diccionario ordenado con la información extraída para cada variable

    Note:
        Utiliza variables globales 'referencias', 'queries' y 'rag_result' para
        almacenar datos intermedios necesarios para la evaluación del sistema RAG.
    """
    load_secrets([".env.file", ".env.secrets"])
    vectorstore = load_vectorstore(embeddings_model=get_embeddings_model(), pdf_file_path=pdf_file_path)

    variables_to_resume = load_variables_to_resume()
    ordered_variables = [list(variable.keys())[0] for variable in variables_to_resume]

    global referencias, queries, rag_result
    referencias = load_ground_truth(file_name)
    queries = load_retriever_queries()
    rag_result = []

    fetch_k = int(os.getenv("DOCUMENTS_TO_RETRIEVE"))
    top_k = int(os.getenv("DOCUMENTS_TO_FETCH"))

    tender_resume = {}

    for variable_info in variables_to_resume:
        summary_variable, summary_variable_info = process_variable(
            variable_info, vectorstore, top_k, fetch_k
        )
        tender_resume[summary_variable] = summary_variable_info

    return {key: tender_resume[key] for key in ordered_variables if key in tender_resume}

def process_variable(variable_info: dict, vectorstore, top_k: int, fetch_k: int) -> tuple:
    """
    Procesa una variable específica para extraer su información del documento.

    Args:
        variable_info (dict): Diccionario con la variable y su definición
        vectorstore: Instancia del almacén de vectores
        top_k (int): Número de documentos a retornar
        fetch_k (int): Número de documentos a recuperar

    Returns:
        tuple: (nombre_variable, información_extraída)
    """
    variable, variable_definition = list(variable_info.items())[0]
    variable_info = add_variable_info(variable, variable_definition, vectorstore, top_k, fetch_k)
    return variable, variable_info

def load_variables_to_resume() -> list:
    """
    Carga la lista de variables a extraer desde un archivo JSON.

    Returns:
        list: Lista de variables y sus definiciones
    """
    with open("backend/variables_to_extract.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    return json_data["variables"]

def add_variable_info(variable: str, variable_definition: str, vectorstore, top_k: int, fetch_k: int) -> str:
    """
    Extrae información específica para una variable utilizando RAG.

    Args:
        variable (str): Nombre de la variable a extraer
        variable_definition (str): Definición de la variable
        vectorstore: Instancia del almacén de vectores
        top_k (int): Número de documentos a retornar
        fetch_k (int): Número de documentos a recuperar

    Returns:
        str: Información extraída para la variable

    Note:
        Agrega la muestra generada a 'rag_result' para evaluación posterior
    """
    rag_query = queries[variable]
    top_documents = extract_top_documents(vectorstore, prompt_request=rag_query, top_k=top_k, fetch_k=fetch_k)
    llm_context = parse_document(top_documents)

    prompt_user = SUMMARIZER_PROMPT_USER.format(
        variable=variable,
        definicion_variable=variable_definition,
        contexto=llm_context
    )
    llm_answer = llm_response(
        prompt_system=SUMMARIZER_PROMPT_SYSTEM,
        prompt_user=prompt_user
    ).choices[0].message.content

    sample = SingleTurnSample(
        user_input=rag_query,
        retrieved_contexts=top_documents,
        response=llm_answer,
        reference=referencias[variable]
    )
    rag_result.append(sample)

    return llm_answer

if __name__ == '__main__':
    """
    Script principal para procesar un documento PDF y evaluar el sistema RAG.

    Ejecuta el proceso de extracción de datos y opcionalmente guarda los resultados
    de la evaluación en un archivo JSON.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_file_dir = os.path.join(base_dir, '..', "pdf_files\\")

    file_name = "document_799.pdf"
    pdf_file_path = pdf_file_dir + file_name
    result = tender_data_extractor(pdf_file_path)

    evaluacion = rag_system_evaluation(rag_result)
    guardar = False

    if guardar:
        evaluacion_save = evaluacion.drop("retrieved_contexts", axis=1)
        evaluacion_save["documento"] = re.search(r'\d+', file_name).group()

        json_file = "evaluacion_rag_v3.json"
        new_data = json.loads(evaluacion_save.to_json(orient="records", force_ascii=False))

        if not os.path.isfile(json_file):
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
        else:
            with open(json_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            existing_data.extend(new_data)
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
          
    