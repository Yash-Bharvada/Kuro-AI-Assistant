"""
Kuro Backend - FastAPI Application
Main entry point for the Kuro AI Assistant
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from termcolor import colored

# Load environment variables
load_dotenv()

# Import Kuro modules
from memory import init_pinecone, retrieve_context
from brain import decide_action, generate_natural_response
from tools import execute_function, AVAILABLE_TOOLS

# Initialize FastAPI
app = FastAPI(
    title="Kuro AI Assistant",
    description="Jarvis-style function-driven AI backend",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class KuroRequest(BaseModel):
    message: str

class KuroResponse(BaseModel):
    reply: str
    function_called: str = None
    success: bool = True

# Initialize Pinecone on startup
@app.on_event("startup")
async def startup_event():
    print(colored("=" * 60, "cyan"))
    print(colored("🚀 KURO AI ASSISTANT - INITIALIZING", "cyan", attrs=["bold"]))
    print(colored("=" * 60, "cyan"))
    
    # Check environment variables
    required_vars = ["GOOGLE_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(colored(f"❌ Missing environment variables: {', '.join(missing_vars)}", "red"))
        print(colored("⚠️ Please create a .env file with required keys", "yellow"))
    else:
        print(colored("✅ Environment variables loaded", "green"))
    
    # Initialize Pinecone
    init_pinecone()
    
    print(colored("=" * 60, "cyan"))
    print(colored("✅ KURO IS READY", "green", attrs=["bold"]))
    print(colored("=" * 60, "cyan"))

# Health Check
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Kuro AI Assistant",
        "version": "1.0.0"
    }

# Main Kuro Endpoint
@app.post("/kuro", response_model=KuroResponse)
async def kuro_endpoint(request: KuroRequest):
    """
    Main AI pipeline:
    1. Retrieve relevant context from memory
    2. Send to Gemini for intent recognition
    3. Execute the decided function
    4. Return natural language response
    """
    
    message = request.message.strip()
    
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    print(colored("\n" + "=" * 60, "cyan"))
    print(colored(f"👤 USER: {message}", "white", attrs=["bold"]))
    print(colored("=" * 60, "cyan"))
    
    try:
        # Step 1: Retrieve Context
        print(colored("🔍 Retrieving context from memory...", "yellow"))
        context = retrieve_context(message, top_k=3)
        
        # Step 2: Decide Action
        print(colored("🧠 Consulting Gemini...", "yellow"))
        decision = decide_action(message, context)
        
        function_name = decision.get("function")
        arguments = decision.get("arguments", {})
        
        # Step 3: Execute Function
        print(colored(f"⚙️ Executing: {function_name}", "yellow"))
        result = execute_function(function_name, arguments)
        
        # Step 4: Generate Response
        reply = generate_natural_response(result)
        
        print(colored(f"🤖 KURO: {reply}", "green", attrs=["bold"]))
        print(colored("=" * 60, "cyan"))
        
        return KuroResponse(
            reply=reply,
            function_called=function_name,
            success=result.get("success", True)
        )
        
    except Exception as e:
        print(colored(f"❌ ERROR: {e}", "red"))
        raise HTTPException(status_code=500, detail=str(e))

# Tools Info Endpoint
@app.get("/tools")
async def get_tools():
    """Return available tools/functions"""
    return {
        "available_tools": AVAILABLE_TOOLS
    }

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
