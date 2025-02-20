from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil
from typing import List
import asyncio
from tender_extractor import tender_data_extractor
from evaluation_pipeline import rag_system_evaluation, load_ground_truth
from chatbot import chatbot_response
from validator import validator_response


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get_resume")
async def get_resume(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_file_dir = os.path.join(base_dir, '..', "tmp")

    # Define PDF file path
    pdf_file_path = os.path.join(pdf_file_dir, file.filename)
    # Save the uploaded file
    with open(pdf_file_path, 'wb') as pdf_file:
        content = await file.read()
        pdf_file.write(content)
    
    # Clean up the PDF and Excel directories after response is sent
    def cleanup():
        os.remove(pdf_file_path)
    
    # Add cleanup function to background tasks
    background_tasks.add_task(cleanup)

    return tender_data_extractor(pdf_file_path)


class ChatRequest(BaseModel):
    vectorstore_name: str
    input_text: str
    chat_history: List[str]

@app.post("/chatbot")
async def stream_chatbot_response(request: ChatRequest):
    vectorstore_name = request.vectorstore_name
    input_text = request.input_text
    chat_history = request.chat_history
    
    # Return a StreamingResponse, passing the generator function
    async def response_generator(chatbot_response):
        # Stream the response chunk by chunk
        for chunk in chatbot_response:
            if 'choices' in chunk:
                chunk_content = chunk['choices'][0]['delta'].get('content', '')
                if chunk_content:
                    yield chunk_content  # Yield each chunk as it's received
                await asyncio.sleep(0.1)
    return StreamingResponse(response_generator(chatbot_response(vectorstore_name, input_text, chat_history)),
                             media_type="text/event-stream")


class ValidateRequest(BaseModel):
    vectorstore_name: str
    input_prompt: str
    input_llm: str

@app.post("/validator")
async def validate_response(request: ValidateRequest):
    vectorstore_name = request.vectorstore_name
    input_prompt = request.input_prompt
    input_llm = request.input_llm

    return validator_response(vectorstore_name, input_prompt, input_llm)


class VectorstoreDeleteRequest(BaseModel):
    vectorstore_name: str

@app.post("/delete-vectorstore")
async def delete_vectorstore(request: VectorstoreDeleteRequest):
    vectorstore_name = request.vectorstore_name
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folder_to_delete = os.path.join(base_dir, '..', "vectorstores", vectorstore_name)
    
    print(folder_to_delete)
    if os.path.isdir(folder_to_delete):
        # Recursively delete the folder and its contents
        shutil.rmtree(folder_to_delete)
        return {"status": "success", "message": f"Folder '{folder_to_delete}' deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Folder '{folder_to_delete}' not found")


@app.post("/get_evaluation")
async def get_evaluation():
    try:
        evaluation_result = rag_system_evaluation()
        return {"evaluation_result": evaluation_result}
    except Exception as e:
        return {"error": str(e)}