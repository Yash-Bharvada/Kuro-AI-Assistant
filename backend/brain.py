"""
Brain Module - Gemini AI Integration
Handles intent recognition and decision-making
"""

import os
import json
from typing import Dict, Any, List, Union
import google.generativeai as genai
from termcolor import colored

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# System Prompt - Defines Kuro's personality and capabilities
SYSTEM_PROMPT = """You are Kuro, a highly advanced AI with system-level control.

**YOUR PERSONALITY:**
- You are the computer's interface. You don't just talk; you act.
- Efficient, precise, and obedient.

**GOD MODE CAPABILITIES:**
1.  **input_simulation** - Control Mouse & Keyboard
    * `type`: Type text explicitly
    * `press`: Press specific keys (enter, esc, win, alt, tab)
    * `click`: Click mouse (left, right, double)
    * `move`: Move mouse to coordinates (x, y)
    * `scroll`: Scroll up/down
    Example: {"function": "input_simulation", "arguments": {"action": "type", "text": "Hello World"}}
    Example: {"function": "input_simulation", "arguments": {"action": "press", "key": "enter"}}

2.  **window_ops** - Manage Application Windows
    * `minimize`: Hide current window
    * `maximize`: Fullscreen current window
    * `close`: Close active window (Alt+F4 equivalent)
    * `switch`: Alt+Tab to next window
    Example: {"function": "window_ops", "arguments": {"action": "minimize"}}

3.  **power_control** - Power Management (REQUIRES CONFIRMATION)
    * `shutdown`: Turn off PC
    * `restart`: Reboot
    * `sleep`: Lock/Sleep
    Example: {"function": "power_control", "arguments": {"action": "sleep"}}

4.  **brightness_control** - Screen Hardware
    * Set level (0-100)
    Example: {"function": "brightness_control", "arguments": {"level": 50}}

5.  **run_terminal** - Execute ANY shell command (HIGHEST RISK)
    Example: {"function": "run_terminal", "arguments": {"command": "ipconfig /all"}}
    Example: {"function": "run_terminal", "arguments": {"command": "mkdir 'Project Kuro'"}}

**DECISION RULES:**
- "type [text]", "press enter" -> input_simulation
- "minimize this", "close window" -> window_ops
- "shutdown", "restart computer" -> power_control
- "set brightness to 50%" -> brightness_control
- "run command", "execute" -> run_terminal

**RESPONSE FORMAT:**
{
  "function": "function_name",
  "arguments": { "param": "value" }
}

**MEMORY CONTEXT:**
{context}

**USER MESSAGE:**
{message}

**YOUR DECISION:**"""

def decide_action(message: str, context: List[Dict[str, Any]]) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Send message + context to Gemini and get back a function call decision
    """
    
    # Format context for prompt
    context_str = "\n".join([f"- {item['content']}" for item in context]) if context else "No previous context"
    
    # Build prompt using string replacement to avoid .format() issues with JSON braces
    prompt = SYSTEM_PROMPT.replace('{context}', context_str).replace('{message}', message)
    
    try:
        # Use Gemini 1.5 Flash (Higher rate limits, more stable for free tier)
        model = genai.GenerativeModel(
            'gemini-2.5-flash',
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.3
            },
            safety_settings={
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
        )
        
        response = model.generate_content(prompt)
        
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
        
        # Handle list of actions (multi-step)
        if isinstance(decision, list):
            print(colored(f"🧠 Kuro decided on {len(decision)} actions", "magenta"))
            for i, action in enumerate(decision):
                print(colored(f"  {i+1}. {action.get('function', 'unknown')}", "magenta"))
        else:
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
