"""
Tools Module - Function Registry for Kuro
Defines all executable functions that Kuro can call
"""

import subprocess
import os
from typing import Dict, Any
from termcolor import colored
from memory import upsert_memory, retrieve_context

# Function Registry
AVAILABLE_TOOLS = {
    "save_memory": {
        "description": "Save important information to long-term memory",
        "parameters": {
            "text": "The information to remember",
            "importance": "high/medium/low",
            "category": "fact/preference/task/other"
        }
    },
    "recall_memory": {
        "description": "Search for specific information in memory",
        "parameters": {
            "query": "What to search for"
        }
    },
    "run_terminal": {
        "description": "Execute ANY shell command (System Level)",
        "parameters": {
            "command": "The command to execute"
        }
    },
    "run_command": {
         "description": "Execute a safe shell command (Alias)",
         "parameters": {
             "command": "The command to execute"
         }
    },
    "open_app": {
        "description": "Open an application",
        "parameters": {
            "app_name": "Name of the application to open"
        }
    },
    "web_scrape": {
        "description": "Open website or scrape content",
        "parameters": {
            "target": "URL or site name",
            "query": "Optional search query"
        }
    },
    "web_search": {
        "description": "Search the web for information",
        "parameters": {
            "query": "What to search for"
        }
    },
    "tell_joke": {
        "description": "Tell a joke to lighten the mood",
        "parameters": {}
    },
    "system_info": {
        "description": "Get system information (battery, CPU, memory, etc.)",
        "parameters": {
            "info_type": "battery/cpu/memory/disk/all"
        }
    },
    "volume_control": {
        "description": "Control system volume",
        "parameters": {
            "action": "up/down/mute/unmute",
            "level": "Optional: volume level 0-100"
        }
    },
    "brightness_control": {
        "description": "Control screen brightness",
        "parameters": {
            "level": "Brightness level 0-100",
            "action": "set/get/up/down"
        }
    },
    "take_screenshot": {
        "description": "Take a screenshot",
        "parameters": {
            "filename": "Optional: filename for the screenshot"
        }
    },
    "input_simulation": {
        "description": "Control Mouse & Keyboard",
        "parameters": {
            "action": "type/press/click/move/scroll",
            "text": "For typing",
            "key": "For pressing",
            "x": "x-coordinate",
            "y": "y-coordinate"
        }
    },
    "window_ops": {
        "description": "Manage Application Windows",
        "parameters": {
            "action": "minimize/maximize/close/switch"
        }
    },
    "power_control": {
        "description": "Power Management",
        "parameters": {
            "action": "shutdown/restart/sleep"
        }
    },
    "reply": {
        "description": "Simple conversational response (no action needed)",
        "parameters": {
            "message": "The response text"
        }
    }
}

def execute_function(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a function based on Gemini's decision"""
    
    print(colored(f"⚙️ Executing: {function_name}", "blue"))
    print(colored(f"   Arguments: {arguments}", "blue"))
    
    try:
        if function_name == "save_memory":
            return save_memory_tool(**arguments)
        elif function_name == "recall_memory":
            return recall_memory_tool(**arguments)
        elif function_name == "run_command" or function_name == "run_terminal":
            return run_command_tool(**arguments)
        elif function_name == "open_app":
            return open_app_tool(**arguments)
        elif function_name == "web_scrape":
            return web_scrape_tool(**arguments)
        elif function_name == "web_search":
            return web_search_tool(**arguments)
        elif function_name == "tell_joke":
            return tell_joke_tool()
        elif function_name == "system_info":
            return system_info_tool(**arguments)
        elif function_name == "volume_control":
            return volume_control_tool(**arguments)
        elif function_name == "brightness_control":
            return brightness_control_tool(**arguments)
        elif function_name == "take_screenshot":
            return take_screenshot_tool(**arguments)
        elif function_name == "input_simulation":
            return input_simulation_tool(**arguments)
        elif function_name == "window_ops":
            return window_ops_tool(**arguments)
        elif function_name == "power_control":
            return power_control_tool(**arguments)
        elif function_name == "reply":
            return reply_tool(**arguments)
        else:
            return {
                "success": False,
                "message": f"Unknown function: {function_name}"
            }
    except Exception as e:
        print(colored(f"❌ Function Execution Error: {e}", "red"))
        return {
            "success": False,
            "message": f"Error executing {function_name}: {str(e)}"
        }

# Tool Implementations

def save_memory_tool(text: str, importance: str = "medium", category: str = "fact") -> Dict[str, Any]:
    """Save information to Pinecone"""
    metadata = {
        "type": category,
        "priority": importance,
        "source": "user"
    }
    success = upsert_memory(text, metadata)
    if success:
        return {"success": True, "message": "Saved.", "natural_response": "Got it. I'll remember that."}
    else:
        return {"success": False, "message": "Failed to save memory", "natural_response": "Sorry, I couldn't save that."}

def recall_memory_tool(query: str) -> Dict[str, Any]:
    """Search memory explicitly"""
    memories = retrieve_context(query, top_k=5)
    if memories:
        results = [m["content"] for m in memories]
        return {"success": True, "message": f"Found {len(memories)} memories", "data": results, "natural_response": f"I found this: {results[0]}"}
    else:
        return {"success": False, "message": "No memories found", "natural_response": "I don't remember anything about that."}

def run_command_tool(command: str) -> Dict[str, Any]:
    """Execute a shell command with safety checks"""
    # Harmful command blocklist
    harmful_keywords = ["rm -rf", "format", "del /s /q", "rd /s /q", "mkfs", "dd if="]
    if any(keyword in command.lower() for keyword in harmful_keywords):
        return {
            "success": False,
            "message": "Harmful command detected",
            "natural_response": "I cannot execute that command as it may be harmful to your system."
        }

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout.strip()
        if not output and result.stderr:
            output = result.stderr.strip()
            
        return {
            "success": True, 
            "message": "Command executed", 
            "data": output, 
            "natural_response": f"Executed: {output[:100]}..." if output else "Command executed."
        }
    except Exception as e:
        return {"success": False, "message": str(e), "natural_response": "Command execution failed."}

def open_app_tool(app_name: str) -> Dict[str, Any]:
    """Open a native application"""
    app_map = {
        "notepad": "notepad.exe", "calculator": "calc.exe", "calc": "calc.exe",
        "explorer": "explorer.exe", "paint": "mspaint.exe", "cmd": "cmd.exe",
        "terminal": "cmd.exe", "powershell": "powershell.exe",
        "settings": "start ms-settings:", "control panel": "control.exe",
        "spotify": "start spotify:", "vscode": "code", "word": "start winword",
        "excel": "start excel", "powerpoint": "start powerpnt", "chrome": "start chrome",
        "browser": "start chrome"
    }
    executable = app_map.get(app_name.lower(), app_name)
    try:
        subprocess.Popen(executable, shell=True)
        return {"success": True, "message": f"Opened {app_name}", "natural_response": f"Opening {app_name}."}
    except Exception as e:
        return {"success": False, "message": str(e), "natural_response": f"Couldn't open {app_name}."}

def web_scrape_tool(target: str, query: str = None) -> Dict[str, Any]:
    import webbrowser
    import urllib.parse
    
    url = target
    if not url.startswith("http"):
         url = f"https://www.google.com/search?q={urllib.parse.quote(target)}"
         
    if query:
        url = f"https://www.google.com/search?q={urllib.parse.quote(target + ' ' + query)}"
        
    webbrowser.open(url)
    return {"success": True, "message": f"Opened {url}", "natural_response": f"Opening {target}."}

def web_search_tool(query: str) -> Dict[str, Any]:
    import webbrowser
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return {"success": True, "message": f"Searching {query}", "natural_response": f"Searching for {query}."}

def tell_joke_tool() -> Dict[str, Any]:
    import random
    jokes = [
        "Why don't programmers like nature? It has too many bugs!",
        "Why do Java developers wear glasses? Because they don't C#!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!"
    ]
    return {"success": True, "natural_response": random.choice(jokes)}

def system_info_tool(info_type: str = "all") -> Dict[str, Any]:
    import psutil
    info = []
    if info_type in ["battery", "all"]:
        b = psutil.sensors_battery()
        if b: info.append(f"Battery: {b.percent}%")
    if info_type in ["cpu", "all"]:
        info.append(f"CPU: {psutil.cpu_percent()}%")
    if info_type in ["memory", "all"]:
        m = psutil.virtual_memory()
        info.append(f"RAM: {m.percent}%")
    return {"success": True, "data": "\n".join(info), "natural_response": f"System status:\n{', '.join(info)}"}

def volume_control_tool(action: str = "set", level: int = None) -> Dict[str, Any]:
    """Control system volume. Uses media keys for up/down to show OSD."""
    try:
        import pyautogui
        
        # Use media keys for relative changes (Triggers Windows OSD)
        if action == "mute" or (action == "set" and level == 0):
            pyautogui.press("volumemute")
            return {"success": True, "natural_response": ""}
            
        elif action == "unmute":
            # Windows toggle behavior is tricky, but 'volumemute' toggles it. 
            # If we want to strictly UNMUTE, we might need pycaw, but let's try toggle first.
           pyautogui.press("volumemute")
           return {"success": True, "natural_response": ""}
           
        elif action == "up":
            # Press multiple times for significant change (e.g., 5 times = ~10%)
            pyautogui.press("volumeup", presses=5) 
            return {"success": True, "natural_response": ""}
            
        elif action == "down":
            pyautogui.press("volumedown", presses=5)
            return {"success": True, "natural_response": ""}
            
        # For setting specific levels, we still need pycaw
        elif level is not None or action == "set":
            target_level = level if level is not None else 50
            
            try:
                # Primary Method: Pycaw (Direct System Control)
                from comtypes import CoInitialize
                CoInitialize() # Initialize COM for this thread (Critical for FastAPI)
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                volume.SetMasterVolumeLevelScalar(target_level / 100.0, None)
                
                # Visual Confirmation (Wiggle)
                pyautogui.press(['volumeup', 'volumedown'])
                return {"success": True, "natural_response": ""}
                
            except Exception as e:
                print(colored(f"⚠️ Pycaw failed ({e}), using key-press fallback...", "yellow"))
                # Fallback Method: Manual Key Presses (Reliable but visual)
                # 1. Reset to 0 (50 taps down roughly covers 100% on most systems)
                pyautogui.press('volumedown', presses=50, interval=0.01)
                
                # 2. Key up to target (Assuming 2% per step, standard Windows behavior)
                steps = int(target_level / 2)
                if steps > 0:
                    pyautogui.press('volumeup', presses=steps, interval=0.01)
                    
                return {"success": True, "natural_response": ""}
            
        return {"success": False, "natural_response": ""}
            
    except Exception as e:
        print(colored(f"❌ Volume Error: {e}", "red"))
        return {"success": False, "natural_response": ""}

def brightness_control_tool(action: str = "set", level: int = None) -> Dict[str, Any]:
    try:
        import screen_brightness_control as sbc
        if action == "get":
            return {"success": True, "natural_response": f"Brightness: {sbc.get_brightness()[0]}%"}
        if action == "set" and level is not None: sbc.set_brightness(level)
        elif action == "up": sbc.set_brightness('+10')
        elif action == "down": sbc.set_brightness('-10')
        return {"success": True, "natural_response": ""}
    except Exception:
        return {"success": False, "natural_response": ""}

def input_simulation_tool(action: str, text: str = None, key: str = None, x: int = None, y: int = None) -> Dict[str, Any]:
    """Simulate Mouse & Keyboard Input"""
    import pyautogui
    try:
        if action == "type" and text:
            pyautogui.write(text, interval=0.05)
        elif action == "press" and key:
            # Handle special keys safely
            pyautogui.press(key)
        elif action == "click":
            pyautogui.click()
        elif action == "move" and x is not None and y is not None:
            pyautogui.moveTo(x, y)
        elif action == "scroll":
            pyautogui.scroll(500) 
        
        return {"success": True, "natural_response": ""}
    except Exception as e:
        return {"success": False, "natural_response": ""}

def window_ops_tool(action: str) -> Dict[str, Any]:
    """Manage Windows"""
    import pyautogui
    try:
        if action == "minimize":
            pyautogui.hotkey('win', 'down')
            pyautogui.hotkey('win', 'down')
        elif action == "maximize":
            pyautogui.hotkey('win', 'up')
        elif action == "close":
            pyautogui.hotkey('alt', 'f4')
        elif action == "switch":
            pyautogui.hotkey('alt', 'tab')
        
        return {"success": True, "natural_response": ""}
    except Exception as e:
        return {"success": False, "natural_response": ""}

def power_control_tool(action: str) -> Dict[str, Any]:
    """Power Management"""
    import os
    try:
        if action == "shutdown":
            os.system("shutdown /s /t 10")
            return {"success": True, "natural_response": "Shutting down in 10 seconds..."}
        elif action == "restart":
            os.system("shutdown /r /t 10")
            return {"success": True, "natural_response": "Restarting in 10 seconds..."}
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return {"success": True, "natural_response": "Going to sleep..."}
        return {"success": False, "natural_response": "Unknown power action."}
    except Exception as e:
        return {"success": False, "natural_response": "Power control failed."}

def take_screenshot_tool(filename: str = None) -> Dict[str, Any]:
    import pyautogui
    from datetime import datetime
    if not filename: filename = f"kuro_screen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    path = os.path.join(os.path.expanduser("~"), "Pictures", filename)
    try:
        pyautogui.screenshot().save(path)
        return {"success": True, "natural_response": f"Screenshot saved to {path}"}
    except Exception as e:
         return {"success": False, "natural_response": f"Screenshot failed: {e}"}

def reply_tool(message: str = None, text: str = None) -> Dict[str, Any]:
    # Support both 'message' (prompt spec) and 'text' (common hallucination)
    response_text = message or text or "I'm here."
    return {"success": True, "message": "Replied", "natural_response": response_text}
