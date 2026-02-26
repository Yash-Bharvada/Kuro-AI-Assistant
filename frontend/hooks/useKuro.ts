"use client";

import { useState, useEffect, useCallback, useRef } from "react";

interface UseKuroReturn {
    isListening: boolean;
    isSpeaking: boolean;
    transcript: string;
    rawTranscript: string;
    start: () => void;
    stop: () => void;
    speak: (text: string) => Promise<number>;
    cancelSpeech: () => void;
    error: string | null;
}

export function useKuro(): UseKuroReturn {
    const [isListening, setIsListening] = useState(false);
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [transcript, setTranscript] = useState("");
    const [rawTranscript, setRawTranscript] = useState("");
    const [error, setError] = useState<string | null>(null);

    const recognitionRef = useRef<any>(null);
    const synthRef = useRef<SpeechSynthesis | null>(null);
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // Silence detection refs
    const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
    const lastSpeechTimeRef = useRef<number>(0);

    // Initialize exactly ONCE on mount
    useEffect(() => {
        if (typeof window === "undefined") return;

        const SpeechRecognition =
            (window as any).SpeechRecognition ||
            (window as any).webkitSpeechRecognition;

        if (!SpeechRecognition) {
            setError("Speech recognition not supported in this browser");
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = true; // Use continuous to manually handle silence
        recognition.interimResults = true; // Needed to track silence
        recognition.lang = "en-US";

        recognition.onresult = (event: any) => {
            const last = event.results.length - 1;
            const text = event.results[last][0].transcript.trim();

            console.log("🎤 Heard (interim):", text);
            setRawTranscript(text);

            // Update last speech time
            lastSpeechTimeRef.current = Date.now();

            // Clear existing timer
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

            // Set new timer for silence (2.5 seconds)
            silenceTimerRef.current = setTimeout(() => {
                console.log("⏳ Silence detected, submitting...");
                recognition.stop();
            }, 2500);
        };

        // Handle final result on end or manually
        recognition.onend = () => {
            console.log("🔴 Recognition ended");
            setIsListening(false);
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

            // If we have a transcript, set it (which triggers submission in page.tsx)
            // Note: we need to access the LATEST rawTranscript here. 
            // Since this is a closure, we rely on the state update in onresult to have happened?
            // Actually, we should probably rely on onresult's final flag if possible, 
            // but since we are forcing stop on silence, let's just use the state.
            // BETTER: Capture the text in a ref to be safe.
        };

        recognition.onerror = (event: any) => {
            if (event.error === "aborted") return;
            if (event.error === "no-speech") {
                setIsListening(false);
                return;
            }
            console.error("Speech recognition error:", event.error);
            setError(`Error: ${event.error}`);
            setIsListening(false);
        };

        recognitionRef.current = recognition;
        synthRef.current = window.speechSynthesis;

        return () => {
            if (recognitionRef.current) recognitionRef.current.abort();
            if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
        };
    }, []);

    // NOTE: We need a way to pass the *final* text out.
    // The current design sets `transcript` state, which page.tsx listens to.
    // In the `onresult` above, we call `setRawTranscript`.
    // When silence is detected, we call `stop()`. `onend` fires.
    // In `onend`, we should promote `rawTranscript` to `transcript` IF it's valid.
    // BUT checking state in `onend` (start closure) is stale.
    // Let's us a ref for the latest text.
    const latestTextRef = useRef("");
    useEffect(() => {
        latestTextRef.current = rawTranscript;
    }, [rawTranscript]);

    // Update onend to use the ref
    useEffect(() => {
        if (recognitionRef.current) {
            recognitionRef.current.onend = () => {
                console.log("🔴 Recognition ended");
                setIsListening(false);
                if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);

                const final = latestTextRef.current.trim();
                if (final) {
                    console.log(`✅ Command detected (silence):`, final);
                    setTranscript(final);
                    setRawTranscript(""); // Clear buffer
                }
            };
        }
    }, [rawTranscript]); // Re-bind onend when transcript updates? No, that's messy.
    // actually, let's just use the ref inside the static onend. 
    // Wait, the static onend defined in mount useEffect cannot see the ref updates if the ref itself isn't stable?
    // useRef object IS stable. So `latestTextRef.current` works fine inside the closure.

    const start = useCallback(() => {
        if (isSpeaking) {
            cancelSpeech(); // Auto-stop speech if mic clicked
        }

        if (recognitionRef.current) {
            try {
                // Clear state
                setTranscript("");
                setRawTranscript("");
                latestTextRef.current = "";
                setError(null);

                recognitionRef.current.start();
                setIsListening(true);
                console.log("🎤 Listening started...");
            } catch (err) {
                console.error("Failed to start:", err);
                if (String(err).includes('already started')) {
                    setIsListening(true);
                } else {
                    setError("Failed to start listening");
                    setIsListening(false);
                }
            }
        }
    }, [isSpeaking]);

    const stop = useCallback(() => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            setIsListening(false); // will trigger onend
        }
    }, []);

    const speak = useCallback(async (text: string): Promise<number> => {
        return new Promise(async (resolve, reject) => {
            try {
                cancelSpeech(); // Stop any previous
                setIsSpeaking(true);

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
                audioRef.current = audio;

                // Wait for metadata to get duration
                audio.onloadedmetadata = () => {
                    const durationMs = audio.duration * 1000;
                    console.log(`🔊 Audio duration: ${durationMs}ms`);
                    // We don't resolve here because we want to play it first? 
                    // No, we want to return duration SOONER so UI can start typing.
                    resolve(durationMs);
                    audio.play().catch(e => console.error("Play error:", e));
                };

                audio.onended = () => {
                    URL.revokeObjectURL(url);
                    setIsSpeaking(false);
                    audioRef.current = null;
                };

                audio.onerror = (e) => {
                    setIsSpeaking(false);
                    audioRef.current = null;
                    console.error("Audio error", e);
                    resolve(0); // Resolve even on error to prevent blocking
                };

                // Fallback if metadata never loads (rare)
                setTimeout(() => {
                    if (!audio.duration) resolve(0);
                }, 5000);

            } catch (error) {
                console.error("TTS Error:", error);
                setIsSpeaking(false);
                resolve(0);
            }
        });
    }, []);

    const cancelSpeech = useCallback(() => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
            audioRef.current = null;
        }
        if (synthRef.current) {
            synthRef.current.cancel();
        }
        setIsSpeaking(false);
    }, []);

    return {
        isListening,
        isSpeaking,
        transcript,
        rawTranscript,
        start,
        stop,
        speak,
        cancelSpeech,
        error,
    };
}
