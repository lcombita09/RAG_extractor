from litellm import completion
import os


def llm_response(prompt_system, prompt_user, stream=False):
  """
    Genera una respuesta utilizando un modelo de lenguaje LLM a través de litellm.

    Esta función configura y realiza una llamada al modelo GPT-4o mini usando la API de OpenAI,
    procesando un prompt de sistema y un prompt de usuario.

    Args:
        prompt_system (str): El mensaje de sistema que establece el contexto o comportamiento
            del modelo
        prompt_user (str): El mensaje o consulta del usuario que el modelo debe responder
        stream (bool, optional): Indica si la respuesta debe ser transmitida en tiempo real.
            Por defecto es False

    Returns:
        dict: Respuesta del modelo que incluye el texto generado y metadatos adicionales

    Note:
        - Requiere que la variable de entorno OPENAI_API_KEY esté configurada
        - Utiliza el modelo 'gpt-4o-mini-2024-07-18'
        - La temperatura está configurada en 0 para respuestas deterministas
        - El límite de tokens está establecido en 512

    Example:
        response = llm_response(
            "Eres un asistente útil",
            "¿Cuál es la capital de Francia?",
            stream=False
        )
    """
    
  os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
  
  return completion(
    model="gpt-4o-mini-2024-07-18",
    messages=[{ "content": prompt_system, "role": "system"},
              { "content": prompt_user, "role": "user"}],
    stream=stream,
    temperature=0,
    max_tokens=512,
  )