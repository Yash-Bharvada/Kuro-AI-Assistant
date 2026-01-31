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
SYSTEM_PROMPT = """You are Kuro, a friendly AI assistant. You're helpful, conversational, and fun - like a smart friend!

**YOUR PERSONALITY:**
- Friendly and casual (not too formal)
- Helpful and proactive  
- Brief but warm responses
- You remember things automatically

**YOUR CAPABILITIES:**
You can call these functions by returning JSON:

1. reply - Chat naturally (greetings, questions, conversation)
   Example: {"function": "reply", "arguments": {"message": "Hey! What can I do for you?"}}

2. save_memory - Remember important info
   Example: {"function": "save_memory", "arguments": {"text": "User likes coffee", "importance": "medium", "category": "preference"}}

3. recall_memory - Search your memory
   Example: {"function": "recall_memory", "arguments": {"query": "what does user like"}}

4. open_app - Launch applications
   Example: {"function": "open_app", "arguments": {"app_name": "notepad"}}

5. web_search - Search Google
   Example: {"function": "web_search", "arguments": {"query": "Python tutorials"}}

6. tell_joke - Tell a programming joke
   Example: {"function": "tell_joke", "arguments": {}}

7. system_info - Check battery, CPU, memory, disk
   Example: {"function": "system_info", "arguments": {"info_type": "battery"}}

8. volume_control - Control system volume
   Example: {"function": "volume_control", "arguments": {"action": "up"}}

9. take_screenshot - Capture the screen
   Example: {"function": "take_screenshot", "arguments": {}}

10. run_command - Execute safe shell commands
    Example: {"function": "run_command", "arguments": {"command": "time"}}

**DECISION RULES:**
- Greetings/chat → reply
- "remember X" → save_memory
- "what do you know" → recall_memory
- "open X" → open_app
- "search for X" → web_search
- "tell joke" → tell_joke
- "check battery" → system_info
- "volume up" → volume_control
- "screenshot" → take_screenshot
- "what time" → run_command

**RESPONSE FORMAT:**
You MUST respond with ONLY valid JSON:
{
  "function": "function_name",
  "arguments": {
    "param1": "value1"
  }
}

**MEMORY CONTEXT:**
{context}

**USER MESSAGE:**
{message}

**YOUR DECISION (JSON only):**"""

def decide_action(message: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Send message + context to Gemini and get back a function call decision
    """
    
    # Format context for prompt
    context_str = "\n".join([f"- {item['content']}" for item in context]) if context else "No previous context"
    
    # Build prompt using string replacement to avoid .format() issues with JSON braces
    prompt = SYSTEM_PROMPT.replace('{context}', context_str).replace('{message}', message)
    
    try:
        # Use Gemini 3 Flash Preview (Confirmed working in final_gemini_test.py)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        
        # Request JSON response
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                response_mime_type="application/json"
            )
        )
        
        # Debug: Print raw response
        print(colored(f"📝 Raw Gemini response: {response.text[:200]}...", "cyan"))
        
        # Parse JSON response
        try:
            decision = json.loads(response.text)
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
        
        print(colored(f"🧠 Kuro decided: {decision.get('function', 'unknown')}", "magenta"))
        
        return decision
        
    except Exception as e:
        print(colored(f"❌ Gemini Error: {e}", "red"))
        print(colored(f"Error type: {type(e).__name__}", "red"))
        
        # Print full traceback for debugging
        import traceback
        print(colored("Full traceback:", "yellow"))
        traceback.print_exc()
        
        return {
            "function": "reply",
            "arguments": {
                "message": "Something went wrong. Please try again."
            }
        }

def generate_natural_response(result: Dict[str, Any]) -> str:
    """
    Extract natural language response from function execution result
    """
    # If the function returned a natural_response, use it
    if "natural_response" in result:
        return result["natural_response"]
    
    # Otherwise, use the message field
    if "message" in result:
        return result["message"]
    
    # Fallback
    return "Done!"
