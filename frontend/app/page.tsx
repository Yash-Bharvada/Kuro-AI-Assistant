"use client";

import { useState, useEffect } from "react";
import { useKuro } from "@/hooks/useKuro";
import { VoicePoweredOrb } from "@/components/ui/voice-powered-orb";
import { KuroCommandDock } from "@/components/KuroCommandDock";
import { AnimatePresence, motion } from "framer-motion";

export default function Home() {
  const kuro = useKuro();
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [listeningState, setListeningState] = useState<'idle' | 'wake-word-detected' | 'processing' | 'responding'>('idle');
  const [lastCommand, setLastCommand] = useState<string>("");
  const [orbColor, setOrbColor] = useState<string | undefined>(undefined);
  const [response, setResponse] = useState<string>("");

  // Check backend status on mount
  useEffect(() => {
    fetch("http://localhost:8000/")
      .then((res) => res.json())
      .then(() => setBackendStatus("online"))
      .catch(() => setBackendStatus("offline"));
  }, []);

  // Auto-start listening on mount if backend is online
  useEffect(() => {
    if (!kuro.isListening && backendStatus === "online") {
      kuro.start();
    }
  }, [backendStatus]);

  // Handle wake word detection and command processing
  useEffect(() => {
    if (kuro.transcript) {
      handleCommand(kuro.transcript);
    }
  }, [kuro.transcript]);

  const handleCommand = async (command: string) => {
    if (!command.trim()) return;

    setLastCommand(command);
    setListeningState('wake-word-detected');
    setOrbColor('#10b981'); // Green for wake word detected

    // Brief delay to show wake word detection
    setTimeout(async () => {
      setListeningState('processing');
      setOrbColor('#3b82f6'); // Blue for processing

      try {
        const response = await fetch("http://localhost:8000/kuro", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: command }),
        });

        if (!response.ok) throw new Error("Backend error");

        const data = await response.json();
        setResponse(data.reply);
        setListeningState('responding');
        setOrbColor('#a855f7'); // Purple for responding

        // Speak the response
        kuro.speak(data.reply);

        // Reset after speaking
        setTimeout(() => {
          setListeningState('idle');
          setOrbColor(undefined);
          setResponse("");
        }, 3000);

      } catch (error) {
        console.error("Error:", error);
        setListeningState('idle');
        setOrbColor('#ef4444'); // Red for error
        kuro.speak("Sorry, I'm having trouble connecting.");

        setTimeout(() => {
          setOrbColor(undefined);
        }, 2000);
      }
    }, 500);
  };

  const handleTextSubmit = (text: string) => {
    handleCommand(text);
  };

  const handleToggleListening = () => {
    if (kuro.isListening) {
      kuro.stop();
      setListeningState('idle');
      setOrbColor(undefined);
    } else {
      kuro.start();
    }
  };

  const getOrbCenterText = () => {
    switch (listeningState) {
      case 'wake-word-detected':
        return 'WAKE WORD DETECTED';
      case 'processing':
        return 'PROCESSING';
      case 'responding':
        return 'RESPONDING';
      default:
        return kuro.isListening ? 'LISTENING' : 'KURO AI';
    }
  };

  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center overflow-hidden">
      {/* Voice Powered Orb Background */}
      <VoicePoweredOrb
        mainColor={orbColor}
        centerText={getOrbCenterText()}
        isTitle={!kuro.isListening && listeningState === 'idle'}
        maxHoverIntensity={listeningState === 'processing' ? 0.8 : 0.5}
        voiceSensitivity={2.0}
        enableVoiceControl={kuro.isListening && listeningState !== 'processing'}
      />

      {/* Response Overlay */}
      <AnimatePresence>
        {response && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="absolute top-1/4 left-1/2 -translate-x-1/2 z-40 max-w-2xl w-full px-4"
          >
            <div className="bg-zinc-900/80 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                  <span className="text-purple-400 text-xl">🤖</span>
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-semibold mb-2">Kuro</h3>
                  <p className="text-white/80 text-sm leading-relaxed">{response}</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Command Dock */}
      <KuroCommandDock
        isListening={kuro.isListening}
        listeningState={listeningState}
        onToggleListening={handleToggleListening}
        onTextSubmit={handleTextSubmit}
        lastCommand={lastCommand}
      />

      {/* Status Indicator */}
      <div className="fixed top-6 right-6 flex items-center gap-2 bg-black/20 backdrop-blur-sm px-4 py-2 rounded-full z-50">
        <div
          className={`w-2 h-2 rounded-full ${backendStatus === "online"
              ? "bg-green-500"
              : backendStatus === "offline"
                ? "bg-red-500"
                : "bg-yellow-500 animate-pulse"
            }`}
        />
        <span className="text-xs text-white/80">
          {backendStatus === "online" ? "Online" : backendStatus === "offline" ? "Offline" : "..."}
        </span>
      </div>

      {/* Error Display */}
      {kuro.error && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 px-4 py-2 bg-red-500/20 border border-red-500/50 rounded-lg backdrop-blur-sm z-50">
          <p className="text-sm text-red-400">{kuro.error}</p>
        </div>
      )}
    </div>
  );
}
