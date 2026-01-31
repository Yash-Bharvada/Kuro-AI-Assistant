# 🤖 Kuro - Jarvis-Style AI Desktop Assistant

A voice-first, function-driven AI assistant that listens, remembers, decides, and acts.

## 🏗️ Architecture

- **Backend**: Python FastAPI (Port 8000)
- **Frontend**: Next.js 14 (Port 3000)
- **Vector DB**: Pinecone (Serverless)
- **AI**: Google Gemini 1.5 Flash + text-embedding-004

---

## 🚀 Quick Start

### 1. Environment Setup

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:

```env
GOOGLE_API_KEY=your_google_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=kuro-memory
PINECONE_ENV=us-east-1
```

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend will run on `http://localhost:8000`

### 3. Frontend Setup

The frontend is already running on port 3000. If you need to restart:

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

---

## 🎯 How to Use

1. **Open the UI**: Navigate to `http://localhost:3000`
2. **Start Listening**: Click "Start Listening" button
3. **Say the Wake Word**: Say "Kuro" followed by your command
   - Example: *"Kuro, remember that my favorite color is blue"*
   - Example: *"Kuro, what's my favorite color?"*
4. **Kuro Responds**: The AI will process your request and respond via voice

---

## 🧠 Core Capabilities

### Voice Interaction
- Continuous microphone listening
- Wake word detection ("Kuro")
- Speech-to-text (browser-based)
- Text-to-speech responses

### Memory System (RAG)
- **Long-term memory** stored in Pinecone
- Automatic context retrieval
- Semantic search with embeddings

### Function Execution
Kuro can execute these functions:

- `save_memory` - Store important information
- `recall_memory` - Search memory
- `run_command` - Execute safe shell commands
- `open_app` - Launch applications
- `reply` - Simple conversational response

---

## 📁 Project Structure

```
Kuro-AI-Assistant/
├── backend/
│   ├── main.py          # FastAPI app & pipeline
│   ├── brain.py         # Gemini AI integration
│   ├── memory.py        # Pinecone vector DB
│   ├── tools.py         # Function registry
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx     # Main UI
│   │   └── globals.css
│   └── hooks/
│       └── useKuro.ts   # Voice hook
└── .env.example
```

---

## 🔧 API Endpoints

### Backend (Port 8000)

- `GET /` - Health check
- `POST /kuro` - Main AI endpoint
  ```json
  {
    "message": "remember that I like pizza"
  }
  ```
- `GET /tools` - List available functions

---

## 🎨 UI Features

- **Cinematic dark mode** (`#05050A`)
- **Animated orb** that pulses when processing
- **Real-time chat history**
- **Backend connection status**
- **Voice controls** with visual feedback

---

## 🛠️ Troubleshooting

### Backend won't start
- Check that all environment variables are set in `.env`
- Verify Python dependencies are installed
- Ensure Pinecone index is created (happens automatically on first run)

### Frontend shows "Offline"
- Make sure backend is running on port 8000
- Check browser console for CORS errors

### Voice not working
- Grant microphone permissions in browser
- Chrome/Edge work best for Web Speech API
- Check browser console for errors

---

## 🔮 Example Commands

Try these with Kuro:

- *"Kuro, remember that my backend uses FastAPI"*
- *"Kuro, what do you know about my backend?"*
- *"Kuro, open notepad"*
- *"Kuro, hello"*

---

## 📝 Notes

- The backend uses **Gemini 1.5 Flash** for fast, intelligent responses
- Memory is stored in **Pinecone** with semantic search
- The UI is built with **Next.js 14** and **Tailwind CSS 4**
- Voice recognition uses the **Web Speech API** (browser-based)

---

## 🚧 Future Enhancements

- Desktop app integration (Electron)
- More function tools (file operations, web search, etc.)
- Multi-language support
- Custom wake word training
- Mobile app version

---

**Built with ❤️ as a Jarvis-inspired AI assistant**
