"use client";

import { useState, useRef } from "react";
import { Mic, Square, Send } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

interface KuroCommandDockProps {
    isListening: boolean;
    listeningState: 'idle' | 'wake-word-detected' | 'processing' | 'responding';
    onToggleListening: () => void;
    onTextSubmit: (text: string) => void;
    lastCommand?: string;
}

export function KuroCommandDock({
    isListening,
    listeningState,
    onToggleListening,
    onTextSubmit,
    lastCommand,
}: KuroCommandDockProps) {
    const [inputValue, setInputValue] = useState("");

    const handleSubmit = () => {
        if (inputValue.trim()) {
            onTextSubmit(inputValue);
            setInputValue("");
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const getStatusText = () => {
        switch (listeningState) {
            case 'wake-word-detected':
                return 'Wake word detected! Listening for command...';
            case 'processing':
                return 'Processing your request...';
            case 'responding':
                return 'Kuro is responding...';
            default:
                return isListening ? 'Listening for "Kuro"...' : 'Click mic to start listening';
        }
    };

    return (
        <motion.div
            initial={{ y: 100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex flex-col items-center gap-3"
        >
            {/* Status Text */}
            <AnimatePresence mode="wait">
                {(isListening || lastCommand) && (
                    <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="text-white/60 text-sm text-center"
                    >
                        {lastCommand ? (
                            <div className="flex flex-col gap-1">
                                <span className="text-white/40 text-xs">Last command:</span>
                                <span className="text-white/80">{lastCommand}</span>
                            </div>
                        ) : (
                            <span>{getStatusText()}</span>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Command Dock */}
            <div className="bg-zinc-900/40 backdrop-blur-xl border border-white/10 rounded-full px-4 py-2 flex items-center gap-3 w-[500px] shadow-2xl shadow-black/50">
                <input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder='Say "Kuro" or type your command...'
                    className="flex-1 bg-transparent outline-none text-white placeholder-zinc-500 font-medium"
                    disabled={listeningState === 'processing' || listeningState === 'responding'}
                />

                <div className="relative">
                    <AnimatePresence mode="wait">
                        {inputValue.trim() ? (
                            <motion.button
                                key="send"
                                initial={{ scale: 0.5, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0.5, opacity: 0 }}
                                onClick={handleSubmit}
                                disabled={listeningState === 'processing'}
                                className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-500 transition-colors disabled:opacity-50"
                            >
                                <Send className="w-5 h-5" />
                            </motion.button>
                        ) : (
                            <motion.button
                                key="mic"
                                initial={{ scale: 0.5, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                exit={{ scale: 0.5, opacity: 0 }}
                                onClick={onToggleListening}
                                disabled={listeningState === 'processing' || listeningState === 'responding'}
                                className={cn(
                                    "p-2 rounded-full transition-all duration-300",
                                    isListening
                                        ? "bg-green-500/20 text-green-500 hover:bg-green-500/30"
                                        : "text-zinc-400 hover:text-white hover:bg-white/5"
                                )}
                            >
                                {isListening ? (
                                    <div className="relative">
                                        <Mic className="w-5 h-5" />
                                        {listeningState === 'wake-word-detected' && (
                                            <span className="absolute inset-0 rounded-full animate-ping bg-green-500/50" />
                                        )}
                                    </div>
                                ) : (
                                    <Mic className="w-5 h-5" />
                                )}
                            </motion.button>
                        )}
                    </AnimatePresence>
                </div>
            </div>
        </motion.div>
    );
}
