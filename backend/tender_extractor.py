import os
import json
import re
import pathlib
import pickle
import pandas as pd
from ragas import SingleTurnSample

from augmented_generator import llm_response
from evaluation_pipeline import rag_system_evaluation, load_ground_truth
from utils import load_secrets, get_embeddings_model
from prompt_engineering import SUMMARIZER_PROMPT_SYSTEM, SUMMARIZER_PROMPT_USER
from retriever import load_vectorstore, extract_top_documents, parse_document, load_retriever_queries


def tender_data_extractor(pdf_file_path):
    # First, load the secrets files to access environmental variables
    load_secrets([".env.file", ".env.secrets"])

    file_name = pathlib.Path(pdf_file_path).name
    
    # Load vectorstore
    vectorstore = load_vectorstore(embeddings_model=get_embeddings_model(), pdf_file_path=pdf_file_path)

    # Variables to resume
    variables_to_resume = load_variables_to_resume()
    ordered_variables = [list(variable.keys())[0] for variable in variables_to_resume]
        
    global referencias 
    referencias = load_ground_truth(file_name)
    
    global queries
    queries =  load_retriever_queries()
    
    # Set number of docs to retrieve
    fetch_k = int(os.getenv("DOCUMENTS_TO_RETRIEVE"))
    top_k = int(os.getenv("DOCUMENTS_TO_FETCH"))

    # Empty dict to return the info of each variable
    tender_resume = {}

    # Objects to evaluate the RAG system.
    global rag_result   
    rag_result = []
    
    for variable_info in variables_to_resume:
        summary_variable, summary_variable_info = process_variable(variable_info, vectorstore, top_k, fetch_k) # Get variable and extracted answer from LLM.
        tender_resume[summary_variable] = summary_variable_info
        
    ordered_tender_resume = {key: tender_resume[key] for key in ordered_variables if key in tender_resume}

    # Guardar la lista en un archivo
    with open("rag_result.pkl", "wb") as f:
        pickle.dump(rag_result, f)

    return ordered_tender_resume

def process_variable(variable_info, vectorstore, top_k, fetch_k):
    variable, variable_definition = list(variable_info.items())[0]
    variable_info = add_variable_info(variable, variable_definition, vectorstore, top_k=top_k, fetch_k=fetch_k)
    return variable, variable_info

def load_variables_to_resume():
    # Load json with variables names
    with open("backend/variables_to_extract.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    return json_data["variables"]

def add_variable_info(variable, variable_definition, vectorstore, top_k, fetch_k):
    # RAG to get context for given variable
    rag_query = queries[variable]
    top_documents = extract_top_documents(vectorstore, prompt_request=rag_query, top_k=top_k, fetch_k=fetch_k)
    llm_context = parse_document(top_documents)
    
    # Generate llm response
    prompt_user = SUMMARIZER_PROMPT_USER.format(variable=variable, definicion_variable= variable_definition, contexto=llm_context)
    llm_answer = llm_response(prompt_system=SUMMARIZER_PROMPT_SYSTEM, prompt_user=prompt_user).choices[0].message.content    
    
    # Sample para Evaluacion
    sample = SingleTurnSample(
        user_input=rag_query,
        retrieved_contexts=top_documents,
        response=llm_answer,
        reference=referencias[variable]
    )
      
    rag_result.append(sample)

    return llm_answer
        

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_file_dir = os.path.join(base_dir, '..', "pdf_files\\")
    
    file_name = "document_852.pdf"
    pdf_file_path = pdf_file_dir + file_name
    print(pdf_file_path)
    result = tender_data_extractor(pdf_file_path)        

    # Rag evaluation
    evaluacion = rag_system_evaluation()
    guardar = False
    
    if guardar:
        evaluacion_save = evaluacion.drop("retrieved_contexts", axis=1)
        evaluacion_save["documento"] = re.search(r'\d+', file_name).group()
        
        json_file = "evaluacion_rag_v3.json"

        # Convertir el DataFrame a una lista de diccionarios
        new_data = json.loads(evaluacion_save.to_json(orient="records", force_ascii=False))

        if not os.path.isfile(json_file):
            # Si no existe, crea un nuevo archivo JSON con un arreglo válido
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, ensure_ascii=False, indent=2)
        else:
            # Si existe, carga los datos existentes, agrega los nuevos y reescribe el archivo
            with open(json_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            existing_data.extend(new_data)
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
          
    