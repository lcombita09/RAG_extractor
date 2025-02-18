import os
from utils import load_secrets, get_embeddings_model
from retriever import load_vectorstore, extract_top_documents, parse_document
from augmented_generator import llm_response
from prompt_engineering import CHATBOT_PROMPT_SYSTEM, CHATBOT_PROMPT_USER


def validator_response(vectorstore_name: str, input_prompt: str, input_llm: str):
    # First, load the secrets files to access environmental variables
    load_secrets([".env.file", ".env.secrets"])

    # Load vectorstore
    vectorstore = load_vectorstore(embeddings_model=get_embeddings_model(), pdf_file_path=f"{vectorstore_name}.pdf")

    # Set number of docs to retrieve
    fetch_k = int(os.getenv("DOCUMENTS_TO_RETRIEVE"))
    top_k = int(os.getenv("DOCUMENTS_TO_FETCH"))

    return generate_validator_response(vectorstore, input_prompt, input_llm, top_k, fetch_k)

def generate_validator_response(vectorstore, input_prompt, input_llm, top_k, fetch_k):
    top_documents = extract_top_documents(vectorstore, prompt_request=input_prompt, top_k=top_k, fetch_k=fetch_k)
    llm_context = parse_document(top_documents)

    # Generate llm response
    prompt_user = CHATBOT_PROMPT_USER.format(question=input_llm, context=llm_context)
    return llm_response(prompt_system=CHATBOT_PROMPT_SYSTEM, prompt_user=prompt_user).choices[0].message.content