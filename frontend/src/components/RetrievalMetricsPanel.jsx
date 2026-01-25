import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const RetrievalMetricsPanel = ({ retrievalMetrics }) => {
    if (!retrievalMetrics) {
        return null;
    }

    const { coverage, diversity, similarity_stats } = retrievalMetrics;

    return (
        <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-700">Retrieval Quality</h3>

            {/* Coverage Score */}
            {coverage && (
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-slate-600">Query Coverage</span>
                        <span className="text-xs font-bold text-indigo-600">
                            {coverage.coverage_percentage.toFixed(0)}%
                        </span>
                    </div>
                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden mb-2">
                        <div
                            className="h-full bg-indigo-500 transition-all"
                            style={{ width: `${coverage.coverage_percentage}%` }}
                        />
                    </div>
                    <div className="text-xs text-slate-500">
                        {coverage.covered_terms.length} of {coverage.num_query_terms} query terms found in chunks
                    </div>
                    {coverage.uncovered_terms.length > 0 && (
                        <div className="mt-2 text-xs text-amber-600">
                            Missing: {coverage.uncovered_terms.slice(0, 3).join(', ')}
                            {coverage.uncovered_terms.length > 3 && ` +${coverage.uncovered_terms.length - 3} more`}
                        </div>
                    )}
                </div>
            )}

            {/* Diversity Score */}
            {diversity && (
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-slate-600">Chunk Diversity</span>
                        <span className="text-xs font-bold text-emerald-600">
                            {(diversity.diversity_score * 100).toFixed(0)}%
                        </span>
                    </div>
                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden mb-2">
                        <div
                            className="h-full bg-emerald-500 transition-all"
                            style={{ width: `${diversity.diversity_score * 100}%` }}
                        />
                    </div>
                    <div className="text-xs text-slate-500 italic">
                        {diversity.interpretation}
                    </div>
                </div>
            )}

            {/* Similarity Statistics */}
            {similarity_stats && (
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs font-medium text-slate-600 mb-2">Similarity Distribution</div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                            <span className="text-slate-500">Mean:</span>
                            <span className="ml-1 font-mono font-semibold text-slate-700">
                                {similarity_stats.mean.toFixed(3)}
                            </span>
                        </div>
                        <div>
                            <span className="text-slate-500">Std:</span>
                            <span className="ml-1 font-mono font-semibold text-slate-700">
                                {similarity_stats.std.toFixed(3)}
                            </span>
                        </div>
                        <div>
                            <span className="text-slate-500">Min:</span>
                            <span className="ml-1 font-mono font-semibold text-slate-700">
                                {similarity_stats.min.toFixed(3)}
                            </span>
                        </div>
                        <div>
                            <span className="text-slate-500">Max:</span>
                            <span className="ml-1 font-mono font-semibold text-slate-700">
                                {similarity_stats.max.toFixed(3)}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* Precision/Recall if available */}
            {retrievalMetrics['precision@5'] !== undefined && (
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="text-xs font-medium text-slate-600 mb-2">Ranking Metrics</div>
                    <div className="space-y-1 text-xs">
                        {Object.entries(retrievalMetrics)
                            .filter(([key]) => key.startsWith('precision@') || key.startsWith('recall@') || key === 'mrr')
                            .map(([key, value]) => (
                                <div key={key} className="flex justify-between">
                                    <span className="text-slate-500">{key.toUpperCase()}:</span>
                                    <span className="font-mono font-semibold text-slate-700">
                                        {value.toFixed(3)}
                                    </span>
                                </div>
                            ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default RetrievalMetricsPanel;
