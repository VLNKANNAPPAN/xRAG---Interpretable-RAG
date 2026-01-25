import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Info, FileText } from 'lucide-react';

const ExplainabilityPanel = ({ explanation }) => {
    if (!explanation) {
        return (
            <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 h-full flex flex-col items-center justify-center text-center text-slate-400">
                <Info className="w-12 h-12 mb-4 opacity-20" />
                <p>Ask a question to see how the AI derived its answer.</p>
            </div>
        );
    }

    const { shap, confidence, source_documents } = explanation;

    // Format data for chart
    const chartData = shap.map(([text, score]) => ({
        name: text.length > 30 ? text.substring(0, 30) + '...' : text,
        fullText: text,
        score: score
    })).sort((a, b) => b.score - a.score).slice(0, 10);

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6 space-y-6 h-full overflow-y-auto">
            <div>
                <h3 className="text-lg font-semibold text-slate-800 mb-2 flex items-center gap-2">
                    <Info className="w-5 h-5 text-indigo-600" />
                    Explainability
                </h3>
                <p className="text-sm text-slate-500 mb-4">
                    Understanding why the model provided this answer.
                </p>

                <div className="bg-slate-50 rounded-lg p-4">
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Confidence Score</div>
                    <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-slate-200 rounded-full overflow-hidden">
                            <div
                                className={`h-full rounded-full ${confidence > 0.7 ? 'bg-emerald-500' : confidence > 0.4 ? 'bg-amber-500' : 'bg-red-500'
                                    }`}
                                style={{ width: `${confidence * 100}%` }}
                            />
                        </div>
                        <span className="font-bold text-slate-700">{(confidence * 100).toFixed(0)}%</span>
                    </div>
                </div>
            </div>

            <div>
                <h4 className="font-medium text-slate-700 mb-3">Top Contributors (SHAP)</h4>
                <div className="h-[200px] w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={chartData} layout="vertical" margin={{ left: 0 }}>
                            <XAxis type="number" hide />
                            <YAxis dataKey="name" type="category" width={100} tick={{ fontSize: 11 }} interval={0} />
                            <Tooltip
                                cursor={{ fill: 'transparent' }}
                                content={({ active, payload }) => {
                                    if (active && payload && payload.length) {
                                        return (
                                            <div className="bg-slate-800 text-white text-xs p-2 rounded shadow-lg max-w-[200px]">
                                                <p className="mb-1 font-bold">Contribution: {payload[0].value.toFixed(3)}</p>
                                                <p>{payload[0].payload.fullText}</p>
                                            </div>
                                        );
                                    }
                                    return null;
                                }}
                            />
                            <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.score > 0 ? '#6366f1' : '#ef4444'} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div>
                <h4 className="font-medium text-slate-700 mb-3">Key Evidence</h4>
                <div className="space-y-3">
                    {/* Use top_chunks if available, otherwise fallback to chartData logic (legacy or simple view) */}
                    {(explanation.top_chunks || chartData.slice(0, 3)).map((item, idx) => {
                        // Adapting to either ChunkInfo shape or simple shape
                        const isRich = !!item.shap_score;
                        const score = isRich ? item.shap_score : item.score;
                        const text = isRich ? item.text : item.fullText;
                        const similarity = isRich ? item.similarity_score : null;
                        const page = isRich ? item.page : null;
                        const source = isRich ? item.source : null;

                        return (
                            <div key={idx} className="text-xs p-3 bg-indigo-50/50 rounded-lg border border-indigo-100">
                                <div className="flex justify-between mb-1 items-start">
                                    <div className="flex flex-col">
                                        <span className="font-semibold text-indigo-700">Chunk {idx + 1}</span>
                                        {source && (
                                            <span className="text-[10px] text-slate-500">
                                                {source} {page ? `(Page ${page})` : ''}
                                            </span>
                                        )}
                                    </div>
                                    <div className="flex flex-col items-end">
                                        <span className="text-indigo-600 font-mono" title="SHAP Contribution">SHAP: {score.toFixed(3)}</span>
                                        {similarity !== null && (
                                            <span className="text-slate-400 font-mono text-[10px]" title="Cosine Similarity">Sim: {similarity.toFixed(3)}</span>
                                        )}
                                    </div>
                                </div>
                                <p className="text-slate-600 line-clamp-3 italic">"{text}"</p>
                            </div>
                        );
                    })}
                </div>
            </div>

            {source_documents && source_documents.length > 0 && (
                <div className="pt-4 border-t border-slate-100">
                    <h4 className="font-medium text-slate-700 mb-2 flex items-center gap-1">
                        <FileText className="w-4 h-4" /> Sources
                    </h4>
                    <div className="flex flex-wrap gap-2">
                        {source_documents.map((doc, idx) => (
                            <span key={idx} className="px-2 py-1 bg-slate-100 text-slate-600 text-xs rounded border border-slate-200">
                                Source {idx + 1}
                            </span>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ExplainabilityPanel;
