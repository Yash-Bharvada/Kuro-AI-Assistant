"use client";

import { useState, useEffect, useCallback, useRef } from "react";

interface UseKuroReturn {
    isListening: boolean;
    transcript: string;
    start: () => void;
    stop: () => void;
    speak: (text: string) => void;
    error: string | null;
}

export function useKuro(): UseKuroReturn {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [error, setError] = useState<string | null>(null);

    const recognitionRef = useRef<any>(null);
    const synthRef = useRef<SpeechSynthesis | null>(null);

    useEffect(() => {
        // Check browser support
        if (typeof window === "undefined") return;

        const SpeechRecognition =
            (window as any).SpeechRecognition ||
            (window as any).webkitSpeechRecognition;

        if (!SpeechRecognition) {
            setError("Speech recognition not supported in this browser");
            return;
        }

        // Initialize Speech Recognition
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onresult = (event: any) => {
            const last = event.results.length - 1;
            const text = event.results[last][0].transcript.trim();

            console.log("🎤 Heard:", text);

            // Wake word detection: "Kuro"
            const lowerText = text.toLowerCase();
            if (lowerText.includes("kuro")) {
                // Extract command after "Kuro"
                const kuroIndex = lowerText.indexOf("kuro");
                const command = text.substring(kuroIndex + 4).trim();

                if (command) {
                    console.log("✅ Wake word detected! Command:", command);
                    setTranscript(command);
                } else {
                    console.log("👋 Wake word detected (no command)");
                    setTranscript(""); // Just wake word, no command
                }
            }
        };

        recognition.onerror = (event: any) => {
            console.error("Speech recognition error:", event.error);
            setError(`Recognition error: ${event.error}`);
        };

        recognition.onend = () => {
            console.log("🔴 Recognition ended");
            if (isListening) {
                // Auto-restart if still supposed to be listening
                recognition.start();
            }
        };

        recognitionRef.current = recognition;
        synthRef.current = window.speechSynthesis;

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, [isListening]);

    const start = useCallback(() => {
        if (recognitionRef.current && !isListening) {
            try {
                recognitionRef.current.start();
                setIsListening(true);
                setError(null);
                console.log("🎤 Listening started...");
            } catch (err) {
                console.error("Failed to start recognition:", err);
                setError("Failed to start listening");
            }
        }
    }, [isListening]);

    const stop = useCallback(() => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop();
            setIsListening(false);
            console.log("🔴 Listening stopped");
        }
    }, [isListening]);

    const speak = useCallback((text: string) => {
        if (synthRef.current) {
            // Cancel any ongoing speech
            synthRef.current.cancel();

            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 1.0;

            synthRef.current.speak(utterance);
            console.log("🔊 Speaking:", text);
        }
    }, []);

    return {
        isListening,
        transcript,
        start,
        stop,
        speak,
        error,
    };
}
