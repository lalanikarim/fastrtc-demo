from fastrtc import Stream, ReplyOnPause, get_stt_model, get_tts_model
import uvicorn
import numpy as np

app = FastAPI()

app.mount("/", StaticFiles(directory="static"), name="static")

def talk(audio: tuple[int, np.ndarray]):
    stt_model = get_stt_model()
    tts_model = get_tts_model()
    text = stt_model.stt(audio)
    for audio_chunk in tts_model.stream_tts_sync(text):
        yield audio_chunk

stream = Stream(
    handler=ReplyOnPause(talk),
    modality="audio",
    mode="send-receive"
)

def main():
    """Start the Uvicorn server with the FastAPI app."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
