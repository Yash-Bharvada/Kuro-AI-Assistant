<div align="center">

# 🤖 KURO AI ASSISTANT
### The Next-Gen Local OS Copilot

[![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/Gemini-1.5%20Flash-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![Pinecone](https://img.shields.io/badge/Pinecone-Vector_DB-black?style=for-the-badge&logo=pinecone&logoColor=white)](https://www.pinecone.io/)

**Bridge the gap between LLMs and your Operating System.**  
Kuro isn't just a chatbot—it's an agent that sees your screen, controls your apps, and remembers your life.

[Features](#-features) • [Quick Start](#-quick-start) • [Tech Stack](#-tech-stack) • [Documentation](#-documentation)

</div>

---

## 🚀 Quick Start

Get Kuro up and running in **seconds** with our unified launcher.

### **The Command**
```powershell
.\start_kuro.bat
```
*> This initializes the Python Backend Neural Core and the Next.js Visual Interface simultaneously.*

---

## ✨ Features

### 🧠 **Active Memory Core**
Kuro doesn't just process; it *remembers*. Powered by **Pinecone** vector database.
- **Store Facts**: *"Remember that my API key is in .env"*
- **Recall Context**: *"What did I say about the project structure?"*

### ⚙️ **System Control**
Direct hardware and OS management. No more digging through settings menus.
- 🔊 **Volume**: *"Set volume to 50%"*
- 🔆 **Brightness**: *"Dim the screen"*
- 🔋 **Power**: *"Put the PC to sleep"* / *"Restart system"*
- 📊 **Stats**: Real-time CPU & RAM monitoring

### 🚀 **Workflow Automation**
- **App Launching**: *"Open Spotify"*, *"Launch VS Code"*
- **Window Management**: *"Minimize this window"*, *"Close Chrome"*
- **Terminal Access**: execute shell commands directly.

### 🌐 **Web Interaction**
- **Search**: *"Find documentation for Next.js 14"*
- **Browse**: *"Open youtube.com"*
- **Simulate Input**: Automated typing and clicking.

---

## 🛠 Tech Stack

### **Backend (The Brain)**
- **Framework**: FastAPI (Python)
- **AI Model**: Google Gemini 2.5 Flash
- **Memory**: Pinecone Vector Database
- **TTS**: Kokoro (High-quality local text-to-speech)
- **Tools**: `pycaw` (Audio), `screen_brightness_control`, `pyautogui`

### **Frontend (The Face)**
- **Framework**: Next.js 14 (App Router)
- **Styling**: TailwindCSS + Framer Motion
- **UI Components**: Lucide React, Shadcn/ui
- **Visuals**: Futuristic "Jarvis-style" interface

---

## 📦 Installation Guide

If you're setting this up for the first time:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Yash-Bharvada/Kuro-AI-Assistant.git
   cd Kuro-AI-Assistant
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   # Create a .env file with your GOOGLE_API_KEY, PINECONE_API_KEY, etc.
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Launch**
   Return to the root directory and run:
   ```powershell
   .\start_kuro.bat
   ```

---

<div align="center">

**Built with ❤️ by Yash Bharvada**  
*Turning Science Fiction into Reality*

</div>
