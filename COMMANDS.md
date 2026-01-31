# 🤖 Kuro AI - Command & Capabilities Guide

Kuro is a powerful, locally-running AI assistant designed to bridge the gap between LLMs and your Operating System. Below is a detailed breakdown of what Kuro can do, categorized for ease of use.

## 🧠 Memory & Knowledge
These commands allow Kuro to learn about you and recall information later.

| Command | Description | Example Queries |
| :--- | :--- | :--- |
| **Store Information** <br>`save_memory` | Saves facts, preferences, or tasks to the Pinecone vector database. | *"Remember that my API key is stored in .env"*<br>*"Note that I prefer dark mode."* |
| **Recall Information** <br>`recall_memory` | Retrieves specific details from long-term memory. | *"What did I tell you about my API key?"*<br>*"Do you know my favorite color?"* |

<br>

## ⚙️ System Control
Direct hardware and OS management capabilities.

| Command | Description | Example Queries |
| :--- | :--- | :--- |
| **Volume Control** <br>`volume_control` | Adjusts system audio levels (Up, Down, Mute, Set Level). | *"Turn it up!"*<br>*"Mute the volume."*<br>*"Set volume to 50%."* |
| **Brightness** <br>`brightness_control` | Controls monitor brightness settings. | *"Dim the screen."*<br>*"Set brightness to max."* |
| **Power Management** <br>`power_control` | Handles power states (Sleep, Restart, Shutdown). | *"Put the computer to sleep."*<br>*"Restart the PC."* |
| **System Stats** <br>`system_info` | Checks real-time hardware status (Battery, CPU, RAM). | *"How much RAM am I using?"*<br>*"Check battery status."* |

<br>

## 🚀 Application & Workflow
Tools for managing apps and windows.

| Command | Description | Example Queries |
| :--- | :--- | :--- |
| **Launch App** <br>`open_app` | Opens installed applications or system tools. | *"Open Spotify."*<br>*"Launch VS Code."*<br>*"Open Calculator."* |
| **Window Management** <br>`window_ops` | Controls active windows (Minimize, Maximize, Close, Switch). | *"Minimize this window."*<br>*"Close this app."* |
| **Terminal access** <br>`run_terminal` | Executes shell commands directly. | *"List files in this folder."*<br>*"Ping google.com"* |

<br>

## 🌐 Web & Input Automation
Interacting with the web and simulating user input.

| Command | Description | Example Queries |
| :--- | :--- | :--- |
| **Web Search** <br>`web_search` | Performs a Google search in your default browser. | *"Search for Next.js 14 documentation."* |
| **Open Website** <br>`web_scrape` | Opens specific URLs directly. | *"Open youtube.com"* |
| **Input Simulation** <br>`input_simulation` | Simulates mouse clicks, typing, or scrolling. | *"Type 'Hello World'"*<br>*"Scroll down."* |
| **Screenshot** <br>`take_screenshot` | Captures and saves a screenshot of the main screen. | *"Take a screenshot."* |

<br>

## 💬 Conversation & Fun
Interactions that define Kuro's personality.

| Command | Description | Example Queries |
| :--- | :--- | :--- |
| **Chat** <br>`reply` | Normal conversation logic using Gemini 1.5 Flash. | *"What is the capital of France?"*<br>*"Write a poem about coding."* |
| **Jokes** <br>`tell_joke` | Tells a programming or general joke. | *"Tell me a joke."* |

---

> **Tip:** You can chain commands naturally. For example, *"Open Spotify and set volume to 30%"* will trigger both `open_app` and `volume_control`.
