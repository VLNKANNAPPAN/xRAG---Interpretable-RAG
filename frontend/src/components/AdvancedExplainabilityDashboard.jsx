import React, { useState } from 'react';
import TrustworthinessPanel from './TrustworthinessPanel';
import CounterfactualView from './CounterfactualView';
import TokenHighlighter from './TokenHighlighter';
import RetrievalMetricsPanel from './RetrievalMetricsPanel';
import EmbeddingSpaceViz from './visualizations/EmbeddingSpaceViz';
import ExplainabilityPanel from './ExplainabilityPanel';
import { Lightbulb, Target, Zap, Shield, GitBranch } from 'lucide-react';

const AdvancedExplainabilityDashboard = ({ explanation }) => {
    const [activeTab, setActiveTab] = useState('overview');

    if (!explanation) {
        return (
            <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 h-full flex flex-col items-center justify-center text-center text-slate-400">
                <Lightbulb className="w-12 h-12 mb-4 opacity-20" />
                <p>Ask a question to see comprehensive explainability analysis.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 h-full flex flex-col">
            {/* Header */}
            <div className="p-4 border-b border-slate-200">
                <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-indigo-600" />
                    Advanced Explainability
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                    Multi-layered transparency into every decision
                </p>
            </div>

            {/* Tabs */}
            <div className="flex-1 overflow-hidden flex flex-col">
                <div className="border-b border-slate-200 px-4">
                    <div className="flex gap-1 overflow-x-auto">
                        <button
                            onClick={() => setActiveTab('overview')}
                            className={`px-3 py-2 text-xs font-medium transition-colors whitespace-nowrap flex items-center gap-1 ${activeTab === 'overview'
                                ? 'text-indigo-600 border-b-2 border-indigo-600'
                                : 'text-slate-600 hover:text-slate-800'
                                }`}
                        >
                            <Zap className="w-3 h-3" />
                            Overview
                        </button>
                        <button
                            onClick={() => setActiveTab('trustworthiness')}
                            className={`px-3 py-2 text-xs font-medium transition-colors whitespace-nowrap flex items-center gap-1 ${activeTab === 'trustworthiness'
                                ? 'text-indigo-600 border-b-2 border-indigo-600'
                                : 'text-slate-600 hover:text-slate-800'
                                }`}
                        >
                            <Shield className="w-3 h-3" />
                            Trust
                        </button>
                        <button
                            onClick={() => setActiveTab('retrieval')}
                            className={`px-3 py-2 text-xs font-medium transition-colors whitespace-nowrap flex items-center gap-1 ${activeTab === 'retrieval'
                                ? 'text-indigo-600 border-b-2 border-indigo-600'
                                : 'text-slate-600 hover:text-slate-800'
                                }`}
                        >
                            <Target className="w-3 h-3" />
                            Retrieval
                        </button>
                        <button
                            onClick={() => setActiveTab('counterfactual')}
                            className={`px-3 py-2 text-xs font-medium transition-colors whitespace-nowrap flex items-center gap-1 ${activeTab === 'counterfactual'
                                ? 'text-indigo-600 border-b-2 border-indigo-600'
                                : 'text-slate-600 hover:text-slate-800'
                                }`}
                        >
                            <GitBranch className="w-3 h-3" />
                            What-If
                        </button>
                    </div>
                </div>

                {/* Tab Content */}
                <div className="flex-1 overflow-y-auto p-4">
                    {activeTab === 'overview' && (
                        <div className="space-y-4">
                            {/* Basic Explainability */}
                            <ExplainabilityPanel explanation={explanation} />

                            {/* Token Highlighting if available */}
                            {explanation.token_attributions && explanation.answer && (
                                <div className="mt-4">
                                    <h4 className="text-sm font-semibold text-slate-700 mb-2">Answer Attribution</h4>
                                    <div className="bg-slate-50 rounded-lg p-3">
                                        <TokenHighlighter
                                            tokenAttributions={explanation.token_attributions}
                                            answer={explanation.answer}
                                        />
                                    </div>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'trustworthiness' && (
                        <TrustworthinessPanel
                            faithfulness_score={explanation.faithfulness_score}
                            faithfulness_reasoning={explanation.faithfulness_reasoning}
                            hallucination_risk={explanation.hallucination_risk}
                            hallucination_reasoning={explanation.hallucination_reasoning}
                            uncertainty_metrics={explanation.uncertainty_metrics}
                            quality_gate_results={explanation.quality_gate_results}
                        />
                    )}


                    {activeTab === 'retrieval' && (
                        <div className="space-y-4">
                            <RetrievalMetricsPanel retrievalMetrics={explanation.retrieval_metrics} />

                            {explanation.embedding_viz_data && (
                                <div className="mt-4">
                                    <h4 className="text-sm font-semibold text-slate-700 mb-2">Embedding Space</h4>
                                    <EmbeddingSpaceViz vizData={explanation.embedding_viz_data} />
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'counterfactual' && (
                        <CounterfactualView counterfactualData={explanation.counterfactual_explanations} />
                    )}
                </div>
            </div>

            {/* Recommendations Footer */}
            {explanation.recommendations && explanation.recommendations.length > 0 && (
                <div className="p-3 border-t border-slate-200 bg-amber-50">
                    <div className="text-xs font-semibold text-amber-800 mb-1">Recommendations</div>
                    <ul className="text-xs text-amber-700 space-y-1">
                        {explanation.recommendations.slice(0, 3).map((rec, idx) => (
                            <li key={idx} className="flex items-start gap-1">
                                <span>•</span>
                                <span>{rec}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default AdvancedExplainabilityDashboard;
