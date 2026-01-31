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
    "run_command": {
        "description": "Execute a shell command (use with caution)",
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
    "take_screenshot": {
        "description": "Take a screenshot",
        "parameters": {
            "filename": "Optional: filename for the screenshot"
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
        elif function_name == "run_command":
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
        elif function_name == "take_screenshot":
            return take_screenshot_tool(**arguments)
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
        return {
            "success": True,
            "message": "Saved.",
            "natural_response": "Got it. I'll remember that."
        }
    else:
        return {
            "success": False,
            "message": "Failed to save memory",
            "natural_response": "Sorry, I couldn't save that."
        }

def recall_memory_tool(query: str) -> Dict[str, Any]:
    """Search memory explicitly"""
    memories = retrieve_context(query, top_k=5)
    
    if memories:
        results = [m["content"] for m in memories]
        return {
            "success": True,
            "message": f"Found {len(memories)} memories",
            "data": results,
            "natural_response": f"I found this: {results[0]}"
        }
    else:
        return {
            "success": False,
            "message": "No memories found",
            "natural_response": "I don't remember anything about that."
        }

def run_command_tool(command: str) -> Dict[str, Any]:
    """Execute a shell command (DANGEROUS - use with caution)"""
    
    # Whitelist of safe commands (expand as needed)
    safe_prefixes = [
        "dir", "ls", "echo", "date", "time", "whoami", "hostname",
        "ipconfig", "ping", "tracert", "netstat", "systeminfo",
        "tasklist", "ver", "path", "cd", "pwd"
    ]
    
    if not any(command.lower().startswith(prefix) for prefix in safe_prefixes):
        return {
            "success": False,
            "message": "Command not in safe list",
            "natural_response": "Hey, I can't run that command for safety reasons. Let's stick to the safe stuff!"
        }
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout.strip()
        return {
            "success": True,
            "message": "Command executed",
            "data": output,
            "natural_response": f"Here you go! {output[:100]}" if output else "Done!"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "natural_response": "Oops, that didn't work. Let me try something else!"
        }

def open_app_tool(app_name: str) -> Dict[str, Any]:
    """Open a native application"""
    
    # Map common app names to executables (Windows-focused)
    # Browsers and websites are handled by web_scrape_tool now
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "paint": "mspaint.exe",
        "cmd": "cmd.exe",
        "terminal": "cmd.exe",
        "powershell": "powershell.exe",
        "task manager": "taskmgr.exe",
        "settings": "start ms-settings:",
        "control panel": "control.exe",
        "spotify": "start spotify:",
        "vscode": "code",
        "vs code": "code",
        "word": "start winword",
        "excel": "start excel",
        "powerpoint": "start powerpnt"
    }
    
    executable = app_map.get(app_name.lower(), app_name)
    
    try:
        subprocess.Popen(executable, shell=True)
        return {
            "success": True,
            "message": f"Opened {app_name}",
            "natural_response": f"Sure thing! Opening {app_name} for you."
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "natural_response": f"Hmm, I couldn't find {app_name}. Is it installed?"
        }

def web_scrape_tool(target: str, query: str = None) -> Dict[str, Any]:
    """
    Open a website or scrape content.
    target: URL or site name (e.g. "youtube", "bbc.com")
    query: Optional search term on that site
    """
    import requests
    from bs4 import BeautifulSoup
    import webbrowser
    import urllib.parse
    
    # 1. Normalize Target to URL
    url = target
    if not url.startswith("http"):
        # simple mapping for common sites
        common_sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "wikipedia": "https://www.wikipedia.org",
            "github": "https://github.com",
            "reddit": "https://www.reddit.com",
            "stackoverflow": "https://stackoverflow.com",
            "bbc": "https://www.bbc.com/news"
        }
        url = common_sites.get(target.lower(), f"https://www.{target}.com")
    
    # 2. Handle Search Query if present
    if query:
        # Special handling for YouTube search
        if "youtube" in url:
            search_url = f"{url}/results?search_query={urllib.parse.quote(query)}"
            webbrowser.open(search_url)
            return {
                "success": True,
                "natural_response": f"Opening YouTube search for '{query}'"
            }
        
        # Google search with site: operator
        domain = url.split("//")[-1].split("/")[0]
        search_q = f"site:{domain} {query}"
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(search_q)}"
        webbrowser.open(search_url)
        return {
            "success": True,
            "natural_response": f"Searching {domain} for '{query}'"
        }
    
    # 3. No Query -> Open Site or Scrape Headline
    # For now, let's open it to be safe, but also try to fetch title
    try:
        webbrowser.open(url)
        
        # Simple scrape to get page title/description for context
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string.strip() if soup.title else "the website"
        
        return {
            "success": True,
            "message": f"Opened {url}",
            "data": {"title": title, "url": url},
            "natural_response": f"Opened {title} ({url})"
        }
    except Exception as e:
        return {
            "success": False, # Fallback but considered partial success as browser likely opened
            "message": f"Opened browser, but scrape failed: {e}",
            "natural_response": f"Opening {target} for you."
        }

def web_search_tool(query: str) -> Dict[str, Any]:
    """Search the web (opens browser with search)"""
    try:
        import webbrowser
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(search_url)
        return {
            "success": True,
            "message": f"Searching for: {query}",
            "natural_response": f"Let me search that for you! Opening browser..."
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "natural_response": "Couldn't open the browser for search."
        }

def tell_joke_tool() -> Dict[str, Any]:
    """Tell a random joke"""
    import random
    jokes = [
        "Why don't programmers like nature? It has too many bugs!",
        "Why do Java developers wear glasses? Because they don't C#!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        "Why did the developer go broke? Because he used up all his cache!",
        "What's a programmer's favorite hangout place? The Foo Bar!",
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "I would tell you a UDP joke, but you might not get it.",
        "A SQL query walks into a bar, walks up to two tables and asks... 'Can I join you?'"
    ]
    joke = random.choice(jokes)
    return {
        "success": True,
        "message": "Joke told",
        "natural_response": f"Alright, here's one: {joke}"
    }

def system_info_tool(info_type: str = "all") -> Dict[str, Any]:
    """Get system information"""
    try:
        import psutil
        import platform
        
        info = []
        
        if info_type in ["battery", "all"]:
            battery = psutil.sensors_battery()
            if battery:
                info.append(f"Battery: {battery.percent}% {'(charging)' if battery.power_plugged else '(on battery)'}")
        
        if info_type in ["cpu", "all"]:
            cpu_percent = psutil.cpu_percent(interval=1)
            info.append(f"CPU Usage: {cpu_percent}%")
        
        if info_type in ["memory", "all"]:
            memory = psutil.virtual_memory()
            info.append(f"Memory: {memory.percent}% used ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)")
        
        if info_type in ["disk", "all"]:
            disk = psutil.disk_usage('/')
            info.append(f"Disk: {disk.percent}% used ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)")
        
        if info_type == "all":
            info.append(f"OS: {platform.system()} {platform.release()}")
        
        result = "\n".join(info)
        return {
            "success": True,
            "message": "System info retrieved",
            "data": result,
            "natural_response": f"Here's what I found: {result}"
        }
    except ImportError:
        return {
            "success": False,
            "message": "psutil not installed",
            "natural_response": "I need the psutil library to check system info. Want me to help you install it?"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "natural_response": "Couldn't get system info right now."
        }

def volume_control_tool(action: str, level: int = None) -> Dict[str, Any]:
    """Control system volume (Windows)"""
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        if action == "mute":
            volume.SetMute(1, None)
            return {"success": True, "natural_response": "Muted!"}
        elif action == "unmute":
            volume.SetMute(0, None)
            return {"success": True, "natural_response": "Unmuted!"}
        elif action == "up":
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
            return {"success": True, "natural_response": "Volume up!"}
        elif action == "down":
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
            return {"success": True, "natural_response": "Volume down!"}
        elif level is not None:
            volume.SetMasterVolumeLevelScalar(level / 100.0, None)
            return {"success": True, "natural_response": f"Set volume to {level}%!"}
    except ImportError:
        return {
            "success": False,
            "natural_response": "I need the pycaw library for volume control. Let me know if you want to install it!"
        }
    except Exception as e:
        return {"success": False, "natural_response": "Couldn't control volume right now."}

def take_screenshot_tool(filename: str = None) -> Dict[str, Any]:
    """Take a screenshot"""
    try:
        import pyautogui
        from datetime import datetime
        
        if not filename:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        screenshot = pyautogui.screenshot()
        filepath = os.path.join(os.path.expanduser("~"), "Pictures", filename)
        screenshot.save(filepath)
        
        return {
            "success": True,
            "message": f"Screenshot saved to {filepath}",
            "natural_response": f"Got it! Screenshot saved to {filepath}"
        }
    except ImportError:
        return {
            "success": False,
            "natural_response": "I need the pyautogui library to take screenshots. Want me to help install it?"
        }
    except Exception as e:
        return {
            "success": False,
            "message": str(e),
            "natural_response": "Couldn't take a screenshot right now."
        }

def reply_tool(message: str) -> Dict[str, Any]:
    """Simple reply (no action)"""
    return {
        "success": True,
        "message": "Reply sent",
        "natural_response": message
    }
