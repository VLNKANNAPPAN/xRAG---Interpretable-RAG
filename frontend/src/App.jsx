import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ChatInterface from './components/ChatInterface';
import AdvancedExplainabilityDashboard from './components/AdvancedExplainabilityDashboard';
import { LayoutGrid, Database, Zap } from 'lucide-react';
import axios from 'axios';

function App() {
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentExplanation, setCurrentExplanation] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleUploadComplete = () => {
    setChatHistory(prev => [...prev, {
      text: "I've processed the uploaded documents. You can now ask questions about them!",
      isUser: false,
      timestamp: new Date()
    }]);
    setRefreshTrigger(prev => prev + 1);
  };

  const handleSendMessage = async (query) => {
    // Add user message
    const newMessage = { text: query, isUser: true, timestamp: new Date() };
    setChatHistory(prev => [...prev, newMessage]);

    setLoading(true);
    setCurrentExplanation(null);

    try {
      const response = await axios.post('http://127.0.0.1:8000/query', { query });
      const data = response.data;

      // Add AI response
      const botResponse = {
        text: data.answer,
        isUser: false,
        timestamp: new Date(),
        refused: data.refused,
        refusal_reasons: data.refusal_reasons,
        warnings: data.warnings,
        confidence: data.confidence
      };

      setChatHistory(prev => [...prev, botResponse]);
      setCurrentExplanation(data);

    } catch (error) {
      console.error("Query error:", error);
      setChatHistory(prev => [...prev, {
        text: "Sorry, I encountered an error connecting to the server.",
        isUser: false,
        timestamp: new Date(),
        warnings: ["Connection failed"]
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans selection:bg-indigo-100">
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-indigo-600 rounded-lg text-white">
                <Zap className="w-5 h-5" />
              </div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-violet-600">
                xRAG Enterprise
              </span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Left Column: File Upload */}
          <div className="col-span-12 lg:col-span-4">
            <FileUpload onUploadComplete={handleUploadComplete} />

            <div className="bg-indigo-900 text-white rounded-xl p-6 relative overflow-hidden mt-6">
              <div className="relative z-10">
                <h3 className="font-bold text-lg mb-2">Pro Tip</h3>
                <p className="text-indigo-200 text-sm">
                  Upload detailed PDF reports for the best explainability results. Shapley values helps you trust the output.
                </p>
              </div>
              <Database className="absolute -bottom-4 -right-4 w-24 h-24 text-indigo-800 opacity-50" />
            </div>
          </div>

          {/* Right Column: Chat Interface */}
          <div className="col-span-12 lg:col-span-8">
            <ChatInterface
              chatHistory={chatHistory}
              onSendMessage={handleSendMessage}
              loading={loading}
            />
          </div>

          {/* Full Width: Advanced Explainability Dashboard */}
          <div className="col-span-12">
            <AdvancedExplainabilityDashboard explanation={currentExplanation} />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
