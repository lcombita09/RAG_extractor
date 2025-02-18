import json
import os

from langchain_openai import ChatOpenAI
from ragas import evaluate, EvaluationDataset # funcion para evaluar
from ragas.llms import LangchainLLMWrapper # evaluador llm
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

load_secrets([".env.file", ".env.secrets"])

def load_ground_truth(file_name: str):    
   # Load json with variables expected answers.
   
    with open("backend/validation.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
        
    json_data = json_data[file_name]["details"]
        
    return json_data


def evaluator_llm():
    
    evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o-mini", temperature=0))
    return evaluator_llm

def semantic_similarity_metric():  
    
    scorer = SemanticSimilarity(embeddings=LangchainEmbeddingsWrapper(get_embeddings_model()))    
    
    return scorer   
    
### Instanciar objetos de las metricas con LLM as a judge con Prompts en español.

def context_recall_metric():    
    
    scorer = LLMContextRecall()
    prompts = scorer.get_prompts()
    
    # Adapt prompts to spanish    
    
    prompts['context_recall_classification_prompt'].examples[0][0].question = "¿Qué me puedes decir sobre Albert Einstein?"
    
    prompts['context_recall_classification_prompt'].examples[0][0].context = (
    "Albert Einstein (14 de marzo de 1879 - 18 de abril de 1955) fue un físico teórico nacido en Alemania, "
    "ampliamente considerado como uno de los científicos más grandes e influyentes de todos los tiempos. "
    "Es más conocido por desarrollar la teoría de la relatividad, pero también realizó importantes contribuciones a la mecánica cuántica, "
    "siendo una figura central en la transformación revolucionaria de la comprensión científica de la naturaleza que logró la física moderna en las primeras décadas del siglo XX. "
    "Su fórmula de equivalencia entre masa y energía, E = mc², derivada de la teoría de la relatividad, "
    "ha sido llamada 'la ecuación más famosa del mundo'. En 1921, recibió el Premio Nobel de Física "
    "'por sus servicios a la física teórica, y especialmente por su descubrimiento de la ley del efecto fotoeléctrico', "
    "un paso clave en el desarrollo de la teoría cuántica. Su trabajo también es reconocido por su influencia en la filosofía de la ciencia. "
    "En una encuesta realizada en 1999 por la revista británica Physics World a 130 físicos destacados de todo el mundo, "
    "Einstein fue clasificado como el mayor físico de todos los tiempos. Sus logros intelectuales y originalidad han convertido a Einstein en sinónimo de genialidad."
    )
    
    prompts['context_recall_classification_prompt'].examples[0][0].answer = (
    "Albert Einstein, nacido el 14 de marzo de 1879, fue un físico teórico de origen alemán, "
    "ampliamente considerado como uno de los científicos más grandes e influyentes de todos los tiempos. "
    "Recibió el Premio Nobel de Física en 1921 por sus servicios a la física teórica. "
    "En 1905, publicó cuatro artículos científicos. En 1895, Einstein se mudó a Suiza."
    )
    
    clasificaciones = [ContextRecallClassification(statement='Albert Einstein, nacido el 14 de marzo de 1879, fue un físico teórico de origen alemán, ampliamente considerado como uno de los científicos más grandes e influyentes de todos los tiempos.', 
                    reason='La fecha de nacimiento de Einstein se menciona claramente en el contexto.', 
                    attributed=1),

                    ContextRecallClassification(statement='Recibió el Premio Nobel de Física en 1921 por sus servicios a la física teórica.', 
                    reason='La oración exacta está presente en el contexto dado.', 
                    attributed=1),

                    ContextRecallClassification(statement='Publicó 4 artículos en 1905.', 
                    reason='No hay mención sobre los artículos que escribió en el contexto dado.', 
                    attributed=0),

                    ContextRecallClassification(statement='Einstein se mudó a Suiza en 1895.', 
                    reason='No hay evidencia que respalde esto en el contexto dado.', 
                    attributed=0)]
    
    prompts['context_recall_classification_prompt'].examples[0][1].classifications = clasificaciones
    prompts['context_recall_classification_prompt'].language = 'español'
    scorer.set_prompts(context_recall_classification_prompt=prompts['context_recall_classification_prompt'])
    return scorer

def context_precision_metric():    
           
    scorer = LLMContextPrecisionWithReference()
    prompts = scorer.get_prompts()
    
    # Adapt prompts to spanish   
        
    prompts['context_precision_prompt'].examples[0][0].question = "¿Qué me puedes decir sobre Albert Einstein?"
    prompts['context_precision_prompt'].examples[1][0].question = "¿Quién ganó la Copa Mundial de la ICC 2020?"
    prompts['context_precision_prompt'].examples[2][0].question = "¿Cuál es la montaña más alta del mundo?"
        
    prompts['context_precision_prompt'].examples[0][0].context = ("Albert Einstein (14 de marzo de 1879 - 18 de abril de 1955) fue un físico teórico nacido en Alemania, "
    "ampliamente considerado uno de los científicos más grandes e influyentes de todos los tiempos. "
    "Es mejor conocido por desarrollar la teoría de la relatividad, pero también hizo contribuciones importantes "
    "a la mecánica cuántica, convirtiéndose en una figura clave en la transformación revolucionaria de la comprensión científica "
    "de la naturaleza que logró la física moderna en las primeras décadas del siglo XX. Su fórmula de equivalencia entre masa y "
    "energía, E = mc², derivada de la teoría de la relatividad, ha sido llamada 'la ecuación más famosa del mundo'. "
    "En 1921, recibió el Premio Nobel de Física 'por sus servicios a la física teórica y, en especial, por su descubrimiento de la ley del efecto fotoeléctrico', "
    "un paso fundamental en el desarrollo de la teoría cuántica. Su trabajo también influyó en la filosofía de la ciencia."
    "En una encuesta de 1999 realizada por la revista británica Physics World entre 130 destacados físicos de todo el mundo, "
    "Einstein fue clasificado como el físico más grande de todos los tiempos. "
    "Sus logros intelectuales y su originalidad han hecho que su nombre sea sinónimo de genio.")

    prompts['context_precision_prompt'].examples[1][0].context = ("La Copa Mundial de Críquet T20 Masculina de la ICC 2022, "
    "celebrada del 16 de octubre al 13 de noviembre de 2022 en Australia, fue la octava edición del torneo. "
    "Originalmente programada para 2020, fue pospuesta debido a la pandemia de COVID-19. "
    "Inglaterra se coronó campeón tras vencer a Pakistán por cinco wickets en la final, "
    "logrando así su segundo título de la Copa Mundial de Críquet T20 Masculina de la ICC.")

    prompts['context_precision_prompt'].examples[2][0].context = ("Los Andes son la cordillera continental más larga del mundo, "
    "ubicada en Sudamérica. Se extiende a lo largo de siete países y alberga muchas de las cumbres más altas del hemisferio occidental. "
    "La cordillera es conocida por sus diversos ecosistemas, que incluyen el Altiplano Andino y la selva amazónica.")

    prompts['context_precision_prompt'].examples[0][0].answer = ("Albert Einstein, nacido el 14 de marzo de 1879, fue un físico teórico de origen alemán, "
    "ampliamente considerado como uno de los científicos más grandes e influyentes de todos los tiempos. "
    "Recibió el Premio Nobel de Física en 1921 por sus contribuciones a la física teórica.")

    prompts['context_precision_prompt'].examples[1][0].answer = "Inglaterra."

    prompts['context_precision_prompt'].examples[2][0].answer = "El Monte Everest."

    prompts['context_precision_prompt'].examples[0][1].reason = ("El contexto proporcionado fue realmente útil para llegar a la respuesta dada. "
    "El contexto incluye información clave sobre la vida y las contribuciones de Albert Einstein, que se reflejan en la respuesta.")

    prompts['context_precision_prompt'].examples[1][1].reason = ("El contexto fue útil para aclarar la situación con respecto a la Copa del Mundo ICC 2020 "
    "e indicar que Inglaterra fue el ganador del torneo que estaba previsto para 2020 pero que en realidad se llevó a cabo en 2022.")

    prompts['context_precision_prompt'].examples[2][1].reason = ("El contexto proporcionado analiza la cordillera de los Andes, "
    "que, si bien es impresionante, no incluye el Monte Everest ni se relaciona directamente con la pregunta sobre la montaña más alta del mundo.")

    prompts['context_precision_prompt'].language = 'español'

    scorer.set_prompts(context_precision_prompt=prompts['context_precision_prompt'])
            
    return scorer

def faithfulness_metric():
        
    scorer = Faithfulness()
    
    prompts = scorer.get_prompts()   
    

    prompts['n_l_i_statement_prompt'].examples[0][0].context = ("John es estudiante de la Universidad XYZ. Está cursando una carrera en Ciencias de la Computación. "
                "Este semestre está inscrito en varias materias, incluyendo Estructuras de Datos, Algoritmos y Gestión de Bases de Datos. "
                "John es un estudiante aplicado y dedica una cantidad significativa de tiempo a estudiar y completar tareas. "
                "A menudo se queda hasta tarde en la biblioteca para trabajar en sus proyectos.")

    prompts['n_l_i_statement_prompt'].examples[0][0].statements = [
        "John está especializándose en Biología.",
        "John está tomando un curso de Inteligencia Artificial.",
        "John es un estudiante dedicado.",
        "John tiene un trabajo a tiempo parcial."
    ]

    prompts['n_l_i_statement_prompt'].examples[0][1].statements[0].statement = "John está especializándose en Biología."
    prompts['n_l_i_statement_prompt'].examples[0][1].statements[0].reason = "La especialidad de John se menciona explícitamente como Ciencias de la Computación. No hay información que sugiera que esté estudiando Biología."

    prompts['n_l_i_statement_prompt'].examples[0][1].statements[1].statement = "John está tomando un curso de Inteligencia Artificial."
    prompts['n_l_i_statement_prompt'].examples[0][1].statements[1].reason = "El contexto menciona los cursos en los que John está actualmente inscrito, y no se menciona Inteligencia Artificial. Por lo tanto, no se puede deducir que John esté tomando un curso de IA."

    prompts['n_l_i_statement_prompt'].examples[0][1].statements[2].statement = "John es un estudiante dedicado."
    prompts['n_l_i_statement_prompt'].examples[0][1].statements[2].reason = "El contexto indica que dedica una cantidad significativa de tiempo a estudiar y completar tareas. Además, menciona que a menudo se queda hasta tarde en la biblioteca para trabajar en sus proyectos, lo que implica dedicación."

    prompts['n_l_i_statement_prompt'].examples[0][1].statements[3].statement = "John tiene un trabajo a tiempo parcial."
    prompts['n_l_i_statement_prompt'].examples[0][1].statements[3].reason = 'No hay información en el contexto que sugiera que John tenga un trabajo a tiempo parcial.'

    prompts['n_l_i_statement_prompt'].examples[1][0].context = "La fotosíntesis es un proceso utilizado por las plantas, las algas y ciertas bacterias para convertir la energía lumínica en energía química."

    prompts['n_l_i_statement_prompt'].examples[1][0].statements = ["Albert Einstein fue un genio."]

    prompts['n_l_i_statement_prompt'].examples[1][1].statements[0].statement = "Albert Einstein fue un genio."
    prompts['n_l_i_statement_prompt'].examples[1][1].statements[0].reason = "El contexto y la afirmación no estan relacionadas."

    prompts['n_l_i_statement_prompt'].language = 'español'

    scorer.set_prompts(n_l_i_statement_prompt=prompts['n_l_i_statement_prompt'])    

    prompts['statement_generator_prompt'].examples[0][0].question = "¿Quién fue Albert Einstein y por qué es conocido?"
    prompts['statement_generator_prompt'].examples[0][0].answer = "Fue un físico teórico nacido en Alemania, ampliamente reconocido como uno de los físicos más grandes e influyentes de todos los tiempos. Es más conocido por desarrollar la teoría de la relatividad, también hizo importantes contribuciones al desarrollo de la teoría de la mecánica cuántica."

    prompts['statement_generator_prompt'].examples[0][1].statements = [
    "Albert Einstein fue un físico teórico nacido en Alemania.",
    "Albert Einstein es reconocido como uno de los físicos más grandes e influyentes de todos los tiempos.",
    "Albert Einstein es conocido por desarrollar la teoría de la relatividad.",
    "Albert Einstein también hizo importantes contribuciones al desarrollo de la teoría de la mecánica cuántica."
    ]

    prompts['statement_generator_prompt'].language = 'español'

    scorer.set_prompts(statement_generator_prompt=prompts['statement_generator_prompt'])
    
    return scorer

def response_relevancy_metric():
    
    scorer = ResponseRelevancy()
    prompts = scorer.get_prompts()
    
    prompts['response_relevance_prompt'].examples[0][0].response = "Albert Einstein nació en Alemania"
    prompts['response_relevance_prompt'].examples[0][1].question = "¿Dónde nació Albert Einstein?"

    prompts['response_relevance_prompt'].examples[1][0].response = "No conozco la característica revolucionaria del smartphone inventado en 2023, ya que no tengo información más allá de 2022."
    prompts['response_relevance_prompt'].examples[1][1].question = "¿Cuál es la característica revolucionaria del smartphone inventado en 2023?"

    prompts['response_relevance_prompt'].language = "spanish"
    
    scorer.set_prompts(response_relevance_prompt=prompts['response_relevance_prompt'])
    
    return scorer


def rag_system_evaluation(evaluation_dataset):
    
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
        metrics=[
                 semantic, 
                 recall, 
                 precision, 
                 faith,
                 relevancy
            ],
        llm=llm_evaluador,      
    )
    
    # results.upload()
    evaluacion = results.to_pandas()
    
    return evaluacion