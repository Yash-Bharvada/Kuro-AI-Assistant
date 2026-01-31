"use client";

import { useState, useEffect } from "react";
import { useKuro } from "@/hooks/useKuro";
import { VoicePoweredOrb } from "@/components/ui/voice-powered-orb";
import { KuroCommandDock } from "@/components/KuroCommandDock";
import { AnimatePresence, motion } from "framer-motion";
import { ResultCard } from "@/components/ResultCard";

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

  // Manual Mode: Do not auto-start listening on mount
  // useEffect(() => {
  //   if (!kuro.isListening && backendStatus === "online") {
  //     kuro.start();
  //   }
  // }, [backendStatus]);

  // Handle wake word detection and command processing
  useEffect(() => {
    if (kuro.transcript) {
      handleCommand(kuro.transcript);
    }
  }, [kuro.transcript]);

  // Safety: If Kuro stops listening (e.g. timeout/error) and we are not processing, reset state
  useEffect(() => {
    if (!kuro.isListening && listeningState === 'idle') {
      // Already idle, do nothing
    } else if (!kuro.isListening && listeningState !== 'processing' && listeningState !== 'responding') {
      // If mic stopped but we are not processing/responding, reset to idle
      setListeningState('idle');
      setOrbColor(undefined);
    }
  }, [kuro.isListening, listeningState]);

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

        // Only speak/show if there is a reply
        if (data.reply) {
          // Generate and start Audio FIRST
          await kuro.speak(data.reply);

          // THEN show text and update state (Syncs text reveal with audio start)
          setResponse(data.reply);
          setListeningState('responding');
          setOrbColor('#a855f7'); // Purple for responding
        } else {
          // If action was silent, just return to idle immediately
          setListeningState('idle');
          setOrbColor(undefined);
        }

        // DO NOT reset state automatically! Persist until user dismisses or talks again.
        // We only reset the visual state when speech ends (optional) or keep it "responding"
        // Let's keep it "responding" while speaking, then "idle" but keep response visible.
        setTimeout(() => {
          setListeningState('idle'); // Just reset the orb state, keep response text
          setOrbColor(undefined);
        }, 3000); // Visual reset only

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
    // If speaking, button acts as STOP
    if (kuro.isSpeaking) {
      kuro.cancelSpeech();
      return;
    }

    // Normal Mic Toggle
    if (kuro.isListening) {
      kuro.stop();
      setListeningState('idle');
      setOrbColor(undefined);
    } else {
      // Clear previous response when starting new session
      setResponse("");
      kuro.start();
    }
  };

  const getOrbCenterText = () => {
    switch (listeningState) {
      case 'wake-word-detected':
        return 'RECORDING';
      case 'processing':
        return 'PROCESSING';
      case 'responding':
        return 'SPEAKING';
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

      {/* Response ResultCard */}
      <AnimatePresence>
        {response && (
          <ResultCard
            transcription={response}
            sentiment="Neutral"
            confidence={0.98}
            language_used="English"
            onClose={() => setResponse("")}
            isSpeaking={listeningState === 'responding' || kuro.isSpeaking}
          />
        )}
      </AnimatePresence>

      {/* Command Dock */}
      <KuroCommandDock
        isListening={kuro.isListening}
        isSpeaking={kuro.isSpeaking} // Pass speaking state
        listeningState={listeningState}
        onToggleListening={handleToggleListening} // Use same handler (it now handles stop speech too)
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

      {/* Debug: Raw Transcript Display */}
      <div className="fixed bottom-4 left-4 max-w-sm text-xs text-white/50 pointer-events-none z-50 font-mono">
        <p>Microphone Input:</p>
        <p className="text-white/90 bg-black/40 p-2 rounded mt-1 min-h-[1.5em]">{kuro.rawTranscript || "..."}</p>
      </div>
    </div>
  );
}
