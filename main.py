from fastapi import FastAPI, StaticFiles
from fastrtc import Stream, ReplyOnPause
import uvicorn
import numpy as np

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

def echo(audio: tuple[int, np.ndarray]):
    """Example handler function for audio processing."""
    yield audio  # Echo the input audio back to the client

# Initialize the Stream with the handler, modality, and mode
stream = Stream(
    handler=ReplyOnPause(echo),
    modality="audio",
    mode="send-receive"
)

# Mount the Stream on the FastAPI app
stream.mount(app)

def main():
    """Start the Uvicorn server with the FastAPI app."""
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
