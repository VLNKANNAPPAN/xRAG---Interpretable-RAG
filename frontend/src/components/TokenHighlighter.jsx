import React from 'react';

const TokenHighlighter = ({ tokenAttributions, answer }) => {
    if (!tokenAttributions || !tokenAttributions.sentence_attributions) {
        return <div className="text-slate-700">{answer}</div>;
    }

    const { sentence_attributions, citations } = tokenAttributions;

    const getColorClass = (intensity) => {
        switch (intensity) {
            case 'very-high':
                return 'bg-indigo-200 border-indigo-300';
            case 'high':
                return 'bg-indigo-100 border-indigo-200';
            case 'medium':
                return 'bg-blue-100 border-blue-200';
            case 'low':
                return 'bg-slate-100 border-slate-200';
            default:
                return 'bg-slate-50 border-slate-100';
        }
    };

    const getCitation = (sentIdx) => {
        const citation = citations.find(c => c.sentence_index === sentIdx);
        return citation ? citation.citation_marker : null;
    };

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2 text-xs text-slate-600 mb-3">
                <span className="font-medium">Color intensity shows contribution strength:</span>
                <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded bg-indigo-200 border border-indigo-300"></div>
                    <span>High</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded bg-blue-100 border border-blue-200"></div>
                    <span>Medium</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded bg-slate-100 border border-slate-200"></div>
                    <span>Low</span>
                </div>
            </div>

            <div className="space-y-2">
                {sentence_attributions.map((sent_attr, idx) => {
                    const citation = getCitation(sent_attr.sentence_index);

                    return (
                        <div
                            key={idx}
                            className={`inline-block mr-1 mb-1 px-2 py-1 rounded border transition-all hover:shadow-sm ${getColorClass(sent_attr.color_intensity)}`}
                            title={`Contribution: ${(sent_attr.contribution_intensity * 100).toFixed(0)}% | Source: Chunk ${sent_attr.source_chunk_index !== null ? sent_attr.source_chunk_index + 1 : 'Unknown'}`}
                        >
                            <span className="text-sm text-slate-800">
                                {sent_attr.sentence}
                                {citation && (
                                    <sup className="ml-1 text-xs font-semibold text-indigo-600">
                                        {citation}
                                    </sup>
                                )}
                            </span>
                        </div>
                    );
                })}
            </div>

            {/* Citation Legend */}
            {citations && citations.length > 0 && (
                <div className="mt-4 pt-4 border-t border-slate-200">
                    <div className="text-xs font-medium text-slate-600 mb-2">Citations:</div>
                    <div className="space-y-1">
                        {citations.slice(0, 5).map((citation, idx) => (
                            <div key={idx} className="text-xs text-slate-600">
                                <span className="font-semibold text-indigo-600">{citation.citation_marker}</span>
                                {' → Chunk '}
                                {citation.chunk_index + 1}
                            </div>
                        ))}
                        {citations.length > 5 && (
                            <div className="text-xs text-slate-500 italic">
                                ... and {citations.length - 5} more citations
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default TokenHighlighter;
