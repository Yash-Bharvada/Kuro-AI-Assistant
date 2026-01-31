"use client";

import { useState, useEffect, useCallback, useRef } from "react";

interface UseKuroReturn {
    isListening: boolean;
    transcript: string;
    rawTranscript: string;
    start: () => void;
    stop: () => void;
    speak: (text: string) => void;
    error: string | null;
}

export function useKuro(): UseKuroReturn {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [rawTranscript, setRawTranscript] = useState("");
    const [error, setError] = useState<string | null>(null);

    const recognitionRef = useRef<any>(null);
    const synthRef = useRef<SpeechSynthesis | null>(null);

    useEffect(() => {
        // Check browser support
        if (typeof window === "undefined") return;

        let mounted = true;

        const SpeechRecognition =
            (window as any).SpeechRecognition ||
            (window as any).webkitSpeechRecognition;

        if (!SpeechRecognition) {
            setError("Speech recognition not supported in this browser");
            return;
        }

        // Initialize Speech Recognition
        const recognition = new SpeechRecognition();
        recognition.continuous = false; // Changed to false for single command mode
        recognition.interimResults = false;
        recognition.lang = "en-US";

        recognition.onresult = (event: any) => {
            if (!mounted) return;
            const last = event.results.length - 1;
            const text = event.results[last][0].transcript.trim();

            console.log("🎤 Heard:", text);
            setRawTranscript(text);

            if (text) {
                console.log(`✅ Command detected:`, text);
                setTranscript(text);
                // Recognition will auto-stop because continuous=false
                setIsListening(false);
            }
        };

        recognition.onerror = (event: any) => {
            if (!mounted) return;

            if (event.error === "aborted") return;
            if (event.error === "no-speech") {
                // Reset if no speech heard so user can try again easily
                setIsListening(false);
                return;
            }

            console.error("Speech recognition error:", event.error);
            setError(`Error: ${event.error}`);
            setIsListening(false);
        };

        recognition.onend = () => {
            console.log("🔴 Recognition ended");
            // No auto-restart! 
            setIsListening(false);
        };

        recognitionRef.current = recognition;
        synthRef.current = window.speechSynthesis;

        if (isListening) {
            try {
                recognition.start();
            } catch (e) {
                console.error("Error starting:", e);
                setIsListening(false);
            }
        }

        return () => {
            mounted = false;
            if (recognitionRef.current) {
                try {
                    recognitionRef.current.abort();
                } catch (e) { }
            }
        };
    }, [isListening]); // Re-run if isListening changes (to start/stop)

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

    const speak = useCallback(async (text: string) => {
        try {
            console.log("🔊 Requesting TTS for:", text);
            const response = await fetch("http://localhost:8000/tts", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            });

            if (!response.ok) throw new Error("TTS request failed");

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            
            audio.onended = () => {
                URL.revokeObjectURL(url);
            };
            
            await audio.play();
            console.log("🔊 Playing audio...");
        } catch (error) {
            console.error("TTS Error:", error);
            // Fallback to browser TTS if backend fails?
            // For now, let's stick to the request: "add this... Kokoro"
            // If it fails, maybe user hasn't set it up right, but we want to try backend first.
        }
    }, []);

    // Ensure voices are loaded (browser quirk)
    useEffect(() => {
        if (typeof window !== "undefined" && window.speechSynthesis) {
            const loadVoices = () => {
                const voices = window.speechSynthesis.getVoices();
                if (voices.length > 0) {
                    console.log(`✅ Loaded ${voices.length} voices`);
                }
            };

            window.speechSynthesis.onvoiceschanged = loadVoices;
            loadVoices(); // Initial check
        }
    }, []);

    return {
        isListening,
        transcript,
        rawTranscript, // Correctly mapping to the rawTranscript state variable
        start,
        stop,
        speak,
        error,
    };
}
