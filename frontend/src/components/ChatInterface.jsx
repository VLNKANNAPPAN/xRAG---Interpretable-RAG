import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, User, Bot, Loader2, AlertTriangle, ShieldAlert } from 'lucide-react';

const ChatInterface = ({ onSendMessage, loading, chatHistory }) => {
    const [query, setQuery] = useState('');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [chatHistory, loading]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!query.trim() || loading) return;
        onSendMessage(query);
        setQuery('');
    };

    return (
        <div className="flex flex-col h-[600px] bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
            <div className="bg-slate-50 border-b border-slate-100 p-4">
                <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                    <Bot className="w-5 h-5 text-indigo-600" />
                    AI Assistant
                </h3>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-6">
                {chatHistory.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-slate-400 text-center p-8">
                        <Bot className="w-12 h-12 mb-4 opacity-20" />
                        <p>Upload documents and ask questions to get started.</p>
                    </div>
                )}

                {chatHistory.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'}`}>
                        <div className={`flex max-w-[80%] gap-3 ${msg.isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${msg.isUser ? 'bg-indigo-100 text-indigo-600' : 'bg-emerald-100 text-emerald-600'}`}>
                                {msg.isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                            </div>

                            <div className={`flex flex-col gap-1 ${msg.isUser ? 'items-end' : 'items-start'}`}>
                                <div className={`p-4 rounded-2xl ${msg.isUser
                                    ? 'bg-indigo-600 text-white rounded-br-none'
                                    : 'bg-slate-100 text-slate-800 rounded-bl-none'
                                    }`}>
                                    {msg.isUser ? (
                                        <p>{msg.text}</p>
                                    ) : (
                                        <div>
                                            {msg.refused ? (
                                                <div className="flex flex-col gap-2">
                                                    <div className="flex items-center gap-2 text-amber-600 font-medium pb-2 border-b border-amber-200/20">
                                                        <ShieldAlert className="w-4 h-4" />
                                                        Response Refused
                                                    </div>
                                                    <p className="text-slate-600">{msg.refusal_reasons?.[0] || "I cannot answer this based on the provided context."}</p>
                                                </div>
                                            ) : (
                                                <div className="markdown-content text-sm text-slate-700">
                                                    <ReactMarkdown
                                                        remarkPlugins={[remarkGfm]}
                                                        components={{
                                                            table: ({ node, ...props }) => <div className="overflow-x-auto my-3"><table className="border-collapse border border-slate-200 w-full text-xs" {...props} /></div>,
                                                            thead: ({ node, ...props }) => <thead className="bg-slate-50" {...props} />,
                                                            th: ({ node, ...props }) => <th className="border border-slate-200 p-2 text-left font-semibold text-slate-700 whitespace-nowrap" {...props} />,
                                                            td: ({ node, ...props }) => <td className="border border-slate-200 p-2 align-top" {...props} />,
                                                            ul: ({ node, ...props }) => <ul className="list-disc pl-4 mb-3 space-y-1" {...props} />,
                                                            ol: ({ node, ...props }) => <ol className="list-decimal pl-4 mb-3 space-y-1" {...props} />,
                                                            li: ({ node, ...props }) => <li className="pl-1" {...props} />,
                                                            p: ({ node, ...props }) => <p className="mb-3 last:mb-0 leading-relaxed" {...props} />,
                                                            strong: ({ node, ...props }) => <strong className="font-semibold text-slate-900" {...props} />,
                                                            h1: ({ node, ...props }) => <h1 className="text-lg font-bold mb-2 mt-4" {...props} />,
                                                            h2: ({ node, ...props }) => <h2 className="text-base font-bold mb-2 mt-3" {...props} />,
                                                            h3: ({ node, ...props }) => <h3 className="text-sm font-bold mb-1 mt-2" {...props} />,
                                                            code: ({ node, inline, className, children, ...props }) => {
                                                                return inline ? (
                                                                    <code className="bg-slate-100 px-1 py-0.5 rounded font-mono text-xs text-indigo-600" {...props}>{children}</code>
                                                                ) : (
                                                                    <code className="block bg-slate-800 text-slate-100 p-2 rounded-lg font-mono text-xs my-2 overflow-x-auto" {...props}>{children}</code>
                                                                )
                                                            }
                                                        }}
                                                    >
                                                        {msg.text}
                                                    </ReactMarkdown>
                                                </div>
                                            )}

                                            {msg.warnings && msg.warnings.length > 0 && (
                                                <div className="mt-3 text-xs bg-amber-50 text-amber-700 p-2 rounded border border-amber-100">
                                                    {msg.warnings.map((w, i) => <div key={i} className="flex items-center gap-1"><AlertTriangle className="w-3 h-3" /> {w}</div>)}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>

                                {!msg.isUser && msg.confidence !== undefined && (
                                    <span className="text-xs text-slate-400 ml-1">
                                        Confidence: {(msg.confidence * 100).toFixed(0)}%
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="flex max-w-[80%] gap-3">
                            <div className="w-8 h-8 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                                <Bot className="w-5 h-5" />
                            </div>
                            <div className="bg-slate-50 p-4 rounded-2xl rounded-bl-none border border-slate-100 flex items-center gap-2 text-slate-500">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                Thinking...
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 border-t border-slate-100 bg-white">
                <form onSubmit={handleSubmit} className="flex gap-2">
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Ask a question about your documents..."
                        className="flex-1 px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={!query.trim() || loading}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white p-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>
        </div>
    );
};

export default ChatInterface;
