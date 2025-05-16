from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import numpy as np
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Import missing components (update paths as needed)
from fastrtc import get_stt_model, get_tts_model
from fastrtc import Stream, ReplyOnPause, AdditionalOutputs

# Load environment variables from .env file
load_dotenv()

# Pydantic model for conversation messages
class Message(BaseModel):
    role: str
    content: str

# Pydantic model for incoming chat message
class ChatMessage(BaseModel):
    message: str

# Global list to store conversation history
conversation_history: List[Message] = []

app = FastAPI()

stt_model = get_stt_model()
tts_model = get_tts_model()

# Initialize chat model with Ollama configuration
chat_model = init_chat_model(
    model="ollama:llama3.2",
    base_url=os.getenv("OLLAMA_API_BASE")
)

def talk(audio: tuple[int, np.ndarray]):
    # Convert audio to text
    prompt = stt_model.stt(audio)
    
    # Create user message and add to conversation history
    user_message = Message(role="user", content=prompt)
    conversation_history.append(user_message.model_dump())
    
    # Get response from chat model
    response = chat_model.invoke(conversation_history)
    
    # Extract content from response
    response_content = response.content if hasattr(response, 'content') else response
    
    # Create bot message and add to conversation history
    bot_message = Message(role="assistant", content=response_content)
    conversation_history.append(bot_message.model_dump())
    
    # Convert text to speech
    for audio_chunk in tts_model.stream_tts_sync(response_content):
        yield audio_chunk

# Initialize ReplyOnPause before setting the stream handler
reply_on_pause = ReplyOnPause(talk)

stream = Stream(
    handler=reply_on_pause,
    modality="audio",
    mode="send-receive"
)

stream.mount(app)

# New endpoint for streaming additional outputs
from fastapi.responses import StreamingResponse

@app.get("/outputs")
async def stream_outputs(webrtc_id: str):
    async def output_stream():
        async for output in stream.output_stream(webrtc_id):
            # Output is an instance of AdditionalOutputs
            # Extract the first argument (e.g., number of detections)
            yield f"data: {output.args[0]}\n\n"
    
    return StreamingResponse(
        output_stream(),
        media_type="text/event-stream"
    )

# Define the input data model for the hook
class InputData(BaseModel):
    webrtc_id: str

# New endpoint to receive text messages and trigger response
@app.post("/input_hook")
async def input_hook(data: InputData):
    webrtc_id = data.webrtc_id

    # Trigger the response
    handler = stream.handlers[webrtc_id]
    if isinstance(handler, ReplyOnPause):
        handler.trigger_response()

    return {"status": "success"}

# New endpoint to receive text messages
@app.post("/chat")
async def receive_message(chat_message: ChatMessage):
    user_message = Message(role="user", content=chat_message.message)
    conversation_history.append(user_message.model_dump())
    
    # Get response from chat model
    response = chat_model.invoke(conversation_history)
    
    # Extract content from response
    response_content = response.content if hasattr(response, 'content') else response
    
    # Create bot message and add to conversation history
    bot_message = Message(role="assistant", content=response_content)
    conversation_history.append(bot_message.model_dump())
    
    # Trigger the response through the ReplyOn
    reply_on_pause.trigger_response()
    
    return {"response": response_content}

app.mount("/static", StaticFiles(directory="static"), name="static")
def main():
    """Start the Uvicorn server with the FastAPI app."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
