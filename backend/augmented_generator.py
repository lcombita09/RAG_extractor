from litellm import completion
import os


def llm_response(prompt_system, prompt_user, stream=False):
  os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
  
  return completion(
    model="gpt-4o-mini-2024-07-18",
    messages=[{ "content": prompt_system, "role": "system"},
              { "content": prompt_user, "role": "user"}],
    stream=stream,
    temperature=0,
    max_tokens=512,
  )