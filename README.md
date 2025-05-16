# FastRTC Voice Chat Demo

## Project Overview
This project provides a real-time voice chat interface using FastRTC for audio communication, integrated with a FastAPI backend and LangChain for conversational AI. The system supports voice and text messaging, with seamless audio processing via STT (Speech-to-Text) and TTS (Text-to-Speech) models.

## Features
- Real-time voice and text chat
- FastRTC audio streaming
- Integration with OLLAMA LLM for conversational responses
- Persistent chat history
- Web interface with message display and controls

## Getting Started
### Prerequisites
- Python 3.8+
- FastAPI
- Uvicorn
- LangChain
- OLLAMA API
- [FastRTC](https://www.fastrtc.org) (WebSocket audio streaming)
- [fastrtc-client.js](https://github.com/lalanikarim/fastrtc-client) (JavaScript client library)

### Installation
1. Clone the repository
2. Install dependencies:
<pre>
pip install fastapi uvicorn langchain pydantic numpy
</pre>
3. Configure environment variables in `.env` file:
<pre>
OLLAMA_API_BASE=http://localhost:11434
</pre>
4. Run the server:
<pre>
python app.py
</pre>

## Usage
### Frontend
1. Open `static/index.html` in a browser
2. Click "Connect" to establish FastRTC connection
3. Use the chat interface to send messages
4. Voice messages are automatically transcribed and responded to by the AI

### Backend
The FastAPI server handles:
- FastRTC signaling
- Audio processing
- Chat history management
- AI response generation

## Dependencies
- FastRTC client library
- OLLAMA LLM model
- STT/TTS models for audio processing
- LangChain for chat model integration

## Contributing
To add new features or improve existing functionality:
1. Review the code structure and architecture
2. Add new features to the FastAPI routes or JavaScript frontend
3. Update documentation in this README
4. Test changes across all components

This project provides a complete end-to-end solution for real-time conversational interfaces using modern web technologies and AI integration.
