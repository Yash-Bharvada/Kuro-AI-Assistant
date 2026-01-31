"""
Brain Module - Gemini AI Integration
Handles intent recognition and decision-making
"""

import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from termcolor import colored

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# System Prompt - Defines Kuro's personality and capabilities
SYSTEM_PROMPT = """You are Kuro, a Jarvis-style AI assistant. You are intelligent, concise, and action-oriented.

**YOUR CORE BEHAVIOR:**
- You respond like Jarvis from Iron Man: brief, professional, helpful
- You NEVER give long explanations unless asked
- You prefer actions over words
- You remember important information automatically

**YOUR CAPABILITIES:**
You can call these functions by returning JSON:

1. save_memory - Store important facts, preferences, or information
   Example: {"function": "save_memory", "arguments": {"text": "User prefers dark mode", "importance": "high", "category": "preference"}}

2. recall_memory - Search your memory for specific information
   Example: {"function": "recall_memory", "arguments": {"query": "user preferences"}}

3. run_command - Execute safe shell commands
   Example: {"function": "run_command", "arguments": {"command": "dir"}}

4. open_app - Launch applications
   Example: {"function": "open_app", "arguments": {"app_name": "notepad"}}

5. reply - Simple conversational response (no action needed)
   Example: {"function": "reply", "arguments": {"message": "Hello! How can I help?"}}

**DECISION RULES:**
- If user shares a fact, preference, or important info → save_memory
- If user asks "what do you know about X" → recall_memory
- If user asks you to open/launch something → open_app
- If user asks you to run a command → run_command
- For simple greetings or questions → reply

**RESPONSE FORMAT:**
You MUST respond with valid JSON in this exact format:
{
  "function": "function_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}

**MEMORY CONTEXT:**
Below is relevant information from your memory. Use it to inform your responses:
{context}

**USER MESSAGE:**
{message}

**YOUR DECISION (JSON only):**"""

def decide_action(message: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Send message + context to Gemini and get back a function call decision
    Returns: {"function": "name", "arguments": {...}}
    """
    
    # Format context
    context_text = "\n".join([
        f"- {mem['content']} (relevance: {mem['score']:.2f})"
        for mem in context[:3]
    ]) if context else "No relevant memories found."
    
    # Build prompt
    prompt = SYSTEM_PROMPT.format(
        context=context_text,
        message=message
    )
    
    try:
        # Use Gemini 1.5 Flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Request JSON response
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,  # Lower temperature for more deterministic responses
                response_mime_type="application/json"
            )
        )
        
        # Parse JSON response
        decision = json.loads(response.text)
        
        print(colored(f"🧠 Kuro decided: {decision['function']}", "magenta"))
        
        return decision
        
    except json.JSONDecodeError as e:
        print(colored(f"❌ JSON Parse Error: {e}", "red"))
        print(colored(f"Raw response: {response.text}", "yellow"))
        
        # Fallback to simple reply
        return {
            "function": "reply",
            "arguments": {
                "message": "I'm having trouble processing that request."
            }
        }
    
    except Exception as e:
        print(colored(f"❌ Gemini Error: {e}", "red"))
        
        return {
            "function": "reply",
            "arguments": {
                "message": "Something went wrong. Please try again."
            }
        }

def generate_natural_response(function_result: Dict[str, Any]) -> str:
    """
    Convert function execution result into a natural language response
    """
    if "natural_response" in function_result:
        return function_result["natural_response"]
    
    if function_result.get("success"):
        return function_result.get("message", "Done.")
    else:
        return function_result.get("message", "Something went wrong.")
