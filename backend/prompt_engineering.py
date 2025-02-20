SUMMARIZER_PROMPT_SYSTEM = """
Eres un asistente útil. Recibes información del contrato de una licitación y se te pide que extraigas la información
de un determinado campo de la licitación. Tu deber es extraer la información de ese campo de una manera resumida.
"""

SUMMARIZER_PROMPT_USER = """
Ante la tarea de extraer información del contrato de una licitación se pide extraer la información de un determinado Campo
del contrato de licitación. Como recurso de apoyo se proporciona la Definición de Campo pero en ningún caso debe formar parte
de la respuesta. Extrae la información del Campo a partir del Contexto. El Contexto contiene la información relevante del
contrato de licitación para extraer la información del Campo. Incluye toda la información relevante del Contexto en la respuesta.
Responde en español. Cuando la respuesta no esté disponible, devuelve 'No se encontro información en el documento'. Devuelve la respuesta directamente
sin poner previamente el nombre del campo.

Campo: {variable}
Definición de campo: {definicion_variable}
Contexto: {contexto}

Respuesta:
"""

GET_CONTEXT_PROMPT_SYSTEM = """
Eres un asistente útil. Recibes una pregunta de un usuario junto con el historial de preguntas anteriores a esta última pregunta.
Si esta última pregunta necesita contexto, reformúlala a partir de las preguntas anteriores para que la pregunta tenga sentido en
sí misma. Si la pregunta tiene el suficiente contexto, devuelve la pregunta tal como la has recibido. 
"""

GET_CONTEXT_PROMPT_USER = """
Un usuario está haciendo preguntas a un chatbot. Si la última pregunta necesita contexto, reformúlala a partir de las preguntas
anteriores para que la pregunta tenga sentido en sí misma. Si la pregunta tiene el suficiente contexto, devuelve la pregunta tal
como la has recibido. El historial de preguntas viene en formato lista, donde los últimos elementos son las preguntas más recientes.
Tu respuesta debe ser en formato string.

Última pregunta: {question}
Historial de preguntas: {history_questions}

Respuesta:
"""

CHATBOT_PROMPT_SYSTEM = """
Eres un asistente útil. El usuario te hace una pregunta que tiene que ver con el contrato de una licitación. A partir de
esa información sobre el contrato de la licitación, responde a la pregunta del usuario. Debes responder en el idioma
de la pregunta.
"""

CHATBOT_PROMPT_USER = """
Recibes una Pregunta relacionada con el contrato de una licitación. En el Contexto tienes la información del contrato de la
licitación necesaria para responder a la Pregunta. Debes responder siempre a la pregunta con el contexto proporcionado. 
Responde en el idioma de la Pregunta.

Pregunta: {question}
Contexto: {context}

Respuesta:
"""