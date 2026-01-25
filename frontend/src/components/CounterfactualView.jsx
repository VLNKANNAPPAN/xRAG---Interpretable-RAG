import React, { useState } from 'react';
import { ChevronDown, ChevronRight, AlertCircle } from 'lucide-react';

const CounterfactualView = ({ counterfactualData }) => {
    const [expandedIndex, setExpandedIndex] = useState(null);

    if (!counterfactualData || !counterfactualData.counterfactuals) {
        return null;
    }

    const { base_answer, counterfactuals, critical_chunks, avg_impact, max_impact } = counterfactualData;

    const getImpactColor = (impact) => {
        if (impact > 0.7) return 'bg-red-100 text-red-700 border-red-300';
        if (impact > 0.4) return 'bg-amber-100 text-amber-700 border-amber-300';
        if (impact > 0.2) return 'bg-blue-100 text-blue-700 border-blue-300';
        return 'bg-slate-100 text-slate-600 border-slate-300';
    };

    const getImpactLabel = (impact) => {
        if (impact > 0.7) return 'Critical';
        if (impact > 0.4) return 'Important';
        if (impact > 0.2) return 'Relevant';
        return 'Minor';
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-700">Counterfactual Analysis</h3>
                <div className="text-xs text-slate-500">
                    {critical_chunks.length} critical chunk{critical_chunks.length !== 1 ? 's' : ''}
                </div>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-2 gap-3">
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500 mb-1">Avg Impact</div>
                    <div className="text-lg font-bold text-slate-700">{(avg_impact * 100).toFixed(0)}%</div>
                </div>
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs text-slate-500 mb-1">Max Impact</div>
                    <div className="text-lg font-bold text-slate-700">{(max_impact * 100).toFixed(0)}%</div>
                </div>
            </div>

            {/* Critical Chunks Alert */}
            {critical_chunks.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="text-xs text-red-700">
                        <p className="font-semibold mb-1">Critical Dependencies Detected</p>
                        <p>The answer heavily relies on {critical_chunks.length} chunk{critical_chunks.length !== 1 ? 's' : ''}. Removing them would significantly change the response.</p>
                    </div>
                </div>
            )}

            {/* Counterfactual List */}
            <div className="space-y-2">
                <div className="text-xs font-medium text-slate-600 mb-2">What if we removed each chunk?</div>
                {counterfactuals.slice(0, 5).map((cf, idx) => (
                    <div key={idx} className={`border rounded-lg overflow-hidden ${getImpactColor(cf.impact_score)}`}>
                        <button
                            onClick={() => setExpandedIndex(expandedIndex === idx ? null : idx)}
                            className="w-full px-3 py-2 flex items-center justify-between hover:opacity-80 transition-opacity"
                        >
                            <div className="flex items-center gap-2">
                                {expandedIndex === idx ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                                <span className="text-xs font-semibold">Chunk {cf.removed_chunk_index + 1}</span>
                                <span className="text-xs px-2 py-0.5 rounded bg-white bg-opacity-50">
                                    {getImpactLabel(cf.impact_score)}
                                </span>
                            </div>
                            <div className="text-xs font-mono font-bold">
                                {(cf.impact_score * 100).toFixed(0)}% impact
                            </div>
                        </button>

                        {expandedIndex === idx && (
                            <div className="px-3 pb-3 space-y-2 bg-white bg-opacity-50">
                                <div>
                                    <div className="text-xs font-medium text-slate-600 mb-1">Removed Chunk:</div>
                                    <div className="text-xs text-slate-700 italic bg-white rounded p-2 line-clamp-3">
                                        "{cf.removed_chunk}"
                                    </div>
                                </div>

                                {cf.counterfactual_answer !== "[No chunks available]" && (
                                    <div>
                                        <div className="text-xs font-medium text-slate-600 mb-1">Answer Without This Chunk:</div>
                                        <div className="text-xs text-slate-700 bg-white rounded p-2 line-clamp-4">
                                            {cf.counterfactual_answer}
                                        </div>
                                    </div>
                                )}

                                <div className="flex items-center justify-between text-xs">
                                    <span className="text-slate-500">Similarity to original:</span>
                                    <span className="font-mono font-semibold">{(cf.similarity_to_base * 100).toFixed(0)}%</span>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {counterfactuals.length > 5 && (
                <div className="text-xs text-center text-slate-500">
                    Showing top 5 of {counterfactuals.length} chunks analyzed
                </div>
            )}
        </div>
    );
};

export default CounterfactualView;
