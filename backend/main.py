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
from tools import execute_function, AVAILABLE_TOOLS, web_scrape_tool
# Add TTS
from tts import tts_engine
from fastapi.responses import Response

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

class TTSRequest(BaseModel):
    text: str

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
        
        # Validate decision structure
        if isinstance(decision, dict):
            # Normalize single decision to list
            actions = [decision]
        elif isinstance(decision, list):
            actions = decision
            if not actions:
                raise ValueError("Empty decision list received")
        else:
            raise ValueError(f"Invalid decision format: expected dict or list, got {type(decision)}")
        
        results = []
        function_names = []
        
        # Step 3: Execute Function(s)
        for action in actions:
            if "function" not in action:
                print(colored(f"⚠️ Skipping invalid action: {action}", "red"))
                continue
                
            function_name = action.get("function")
            arguments = action.get("arguments", {})
            function_names.append(function_name)
            
            print(colored(f"⚙️ Executing: {function_name}", "yellow"))
            result = execute_function(function_name, arguments)
            results.append(result)
        
        # Step 4: Generate Response
        # If multiple actions, we might want to synthesize a combined response
        # For now, let's pass the list of results to the natural response generator
        # Note: generate_natural_response expects a SINGLE dict currently.
        # We'll pass the LAST valid result for now, but in future should handle combo.
        # Correction: Let's combine the outputs if possible, or just pick the last one.
        # Better approach: Pass a synthetic result combining them.
        
        if len(results) == 1:
            final_result = results[0]
        else:
            final_result = {
                "success": all(r.get("success", False) for r in results),
                "output": "\n".join([str(r.get("output", "")) for r in results]),
                "function": "multi_action"
            }
        
        reply = generate_natural_response(final_result)
        
        print(colored(f"🤖 KURO: {reply}", "green", attrs=["bold"]))
        print(colored("=" * 60, "cyan"))
        
        return KuroResponse(
            reply=reply,
            function_called=",".join(function_names),
            success=final_result.get("success", True)
        )
        
    except Exception as e:
        error_msg = str(e)
        print(colored(f"❌ ERROR: {error_msg}", "red"))
        print(colored(f"Error type: {type(e).__name__}", "red"))
        
        reply_msg = "Sorry, I'm having trouble processing that right now. Can you try again?"
        
        # Check for Quota/Rate Limit Errors
        if "429" in error_msg or "ResourceExhausted" in error_msg:
             reply_msg = "I've hit my brain's thinking limit (Quota Exceeded). Please check your Gemini API keys or try again later."
        
        # Return a friendly error response instead of raising HTTP exception
        return KuroResponse(
            reply=reply_msg,
            function_called="error",
            success=False
        )

@app.post("/tts")
async def tts_endpoint(request: TTSRequest):
    """Generate audio from text using Groq TTS"""
    if not request.text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        audio_buffer = tts_engine.generate_audio(request.text)
        if not audio_buffer:
             raise HTTPException(status_code=500, detail="Failed to generate audio")
             
        # Return as streaming response or direct bytes
        return Response(content=audio_buffer.read(), media_type="audio/wav")
    except Exception as e:
        print(colored(f"❌ TTS Error: {e}", "red"))
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
