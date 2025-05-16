from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import numpy as np
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import json

from fastrtc import get_stt_model, get_tts_model
from fastrtc import Stream, ReplyOnPause, AdditionalOutputs

load_dotenv()

class Message(BaseModel):
    role: str
    content: str

class ChatMessage(BaseModel):
    message: str

conversation_history: List[Message] = []

app = FastAPI()

stt_model = get_stt_model()
tts_model = get_tts_model()

chat_model = init_chat_model(
    model="ollama:llama3.2",
    base_url=os.getenv("OLLAMA_API_BASE")
)

def talk(audio: tuple[int, np.ndarray]):
    if np.shape(audio[1])[1] == 0:
        if conversation_history:
            tts_content = conversation_history[-1].content
            for audio_chunk in tts_model.stream_tts_sync(tts_content):
                yield audio_chunk
        return

    prompt = stt_model.stt(audio)
    user_message = Message(role="user", content=prompt)
    conversation_history.append(user_message.model_dump())
    yield AdditionalOutputs(user_message.model_dump())

    response = chat_model.invoke(conversation_history)
    response_content = response.content if hasattr(response, 'content') else response
    bot_message = Message(role="assistant", content=response_content)
    conversation_history.append(bot_message.model_dump())
    yield AdditionalOutputs(bot_message.model_dump())

    for audio_chunk in tts_model.stream_tts_sync(response_content):
        yield audio_chunk

reply_on_pause = ReplyOnPause(talk)
stream = Stream(
    handler=reply_on_pause,
    modality="audio",
    mode="send-receive"
)

from fastapi.responses import StreamingResponse

@app.get("/outputs")
async def stream_outputs(webrtc_id: str):
    async def output_stream():
        async for output in stream.output_stream(webrtc_id):
            yield f"data: {json.dumps(output.args[0])}\n\n"
    return StreamingResponse(output_stream(), media_type="text/event-stream")

class InputData(BaseModel):
    webrtc_id: str

@app.post("/input_hook")
async def input_hook(data: InputData):
    webrtc_id = data.webrtc_id
    handler = stream.handlers[webrtc_id]
    if isinstance(handler, ReplyOnPause):
        handler.trigger_response()
    return {"status": "success"}

@app.post("/chat")
async def receive_message(chat_message: ChatMessage):
    user_message = Message(role="user", content=chat_message.message)
    conversation_history.append(user_message.model_dump())
    response = chat_model.invoke(conversation_history)
    response_content = response.content if hasattr(response, 'content') else response
    bot_message = Message(role="assistant", content=response_content)
    conversation_history.append(bot_message.model_dump())
    return {"response": response_content}

app.mount("/static", StaticFiles(directory="static"), name="static")

def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
