import json
import os
from langchain_openai import ChatOpenAI
import pandas as pd
from ragas import evaluate, EvaluationDataset
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics._context_recall import ContextRecallClassification
from ragas.metrics import (
    LLMContextRecall,
    LLMContextPrecisionWithReference,
    Faithfulness,
    ResponseRelevancy,
    SemanticSimilarity,
)
from utils import get_embeddings_model, load_secrets

def load_ground_truth(file_name: str) -> dict:
    """
    Carga los datos de validación desde un archivo JSON.

    Args:
        file_name (str): Nombre del archivo de validación

    Returns:
        dict: Datos de validación para el archivo especificado
    """
    with open("backend/validation.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    return json_data[file_name]["details"]

def evaluator_llm() -> LangchainLLMWrapper:
    """
    Inicializa el modelo LLM evaluador.

    Returns:
        LangchainLLMWrapper: Instancia del modelo evaluador configurado
    """
    return LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))

def semantic_similarity_metric() -> SemanticSimilarity:
    """
    Configura la métrica de similitud semántica.

    Returns:
        SemanticSimilarity: Instancia configurada del evaluador de similitud semántica
    """
    return SemanticSimilarity(embeddings=LangchainEmbeddingsWrapper(get_embeddings_model()))

def context_recall_metric() -> LLMContextRecall:
    """
    Configura la métrica de recall del contexto con prompts en español.

    Personaliza los ejemplos y clasificaciones para la evaluación en español.

    Returns:
        LLMContextRecall: Instancia configurada del evaluador de recall
    """
    scorer = LLMContextRecall()
    prompts = scorer.get_prompts()
    # [Configuración detallada de prompts en español...]
    return scorer

def context_precision_metric() -> LLMContextPrecisionWithReference:
    """
    Configura la métrica de precisión del contexto con prompts en español.

    Personaliza los ejemplos y evaluaciones para la medición de precisión en español.

    Returns:
        LLMContextPrecisionWithReference: Instancia configurada del evaluador de precisión
    """
    scorer = LLMContextPrecisionWithReference()
    prompts = scorer.get_prompts()
    # [Configuración detallada de prompts en español...]
    return scorer

def faithfulness_metric() -> Faithfulness:
    """
    Configura la métrica de fidelidad con prompts en español.

    Establece ejemplos y criterios para evaluar la fidelidad de las respuestas.

    Returns:
        Faithfulness: Instancia configurada del evaluador de fidelidad
    """
    scorer = Faithfulness()
    prompts = scorer.get_prompts()
    # [Configuración detallada de prompts en español...]
    return scorer

def response_relevancy_metric() -> ResponseRelevancy:
    """
    Configura la métrica de relevancia de respuesta con prompts en español.

    Establece criterios para evaluar la relevancia de las respuestas generadas.

    Returns:
        ResponseRelevancy: Instancia configurada del evaluador de relevancia
    """
    scorer = ResponseRelevancy()
    prompts = scorer.get_prompts()
    # [Configuración detallada de prompts en español...]
    return scorer

def rag_system_evaluation(evaluation_dataset) -> pd.DataFrame:
    """
    Realiza una evaluación completa del sistema RAG utilizando múltiples métricas.

    Esta función coordina la evaluación del sistema RAG utilizando diferentes métricas
    incluyendo similitud semántica, recall, precisión, fidelidad y relevancia.

    Args:
        evaluation_dataset: Dataset con muestras para evaluación

    Returns:
        pd.DataFrame: DataFrame con los resultados de la evaluación

    Note:
        Requiere la variable de entorno RAGAS_APP_TOKEN configurada
    """
    semantic = semantic_similarity_metric()
    recall = context_recall_metric()
    precision = context_precision_metric()
    faith = faithfulness_metric()
    relevancy = response_relevancy_metric()

    dataset = EvaluationDataset(samples=evaluation_dataset)
    llm_evaluador = evaluator_llm()

    os.environ["RAGAS_APP_TOKEN"] = os.getenv("RAGAS_APP_TOKEN")

    results = evaluate(
        dataset=dataset,
        metrics=[semantic, recall, precision, faith, relevancy],
        llm=llm_evaluador,
    )

    results.upload()
    
    return results.to_pandas()