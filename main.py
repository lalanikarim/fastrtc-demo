from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import numpy as np

# Import missing components (update paths as needed)
from fastrtc import get_stt_model, get_tts_model
from fastrtc import Stream, ReplyOnPause

app = FastAPI()


stt_model = get_stt_model()
tts_model = get_tts_model()

def talk(audio: tuple[int, np.ndarray]):
    text = stt_model.stt(audio)
    for audio_chunk in tts_model.stream_tts_sync(text):
        yield audio_chunk

stream = Stream(
    handler=ReplyOnPause(talk),
    modality="audio",
    mode="send-receive"
)

stream.mount(app)
app.mount("/", StaticFiles(directory="static"), name="static")

def main():
    """Start the Uvicorn server with the FastAPI app."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
