import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, XCircle, Info, ChevronDown, ChevronUp } from 'lucide-react';

const TrustworthinessPanel = ({
    faithfulness_score,
    faithfulness_reasoning,
    hallucination_risk,
    hallucination_reasoning,
    uncertainty_metrics,
    quality_gate_results
}) => {
    const [showFaithfulnessDetails, setShowFaithfulnessDetails] = useState(false);
    const [showHallucinationDetails, setShowHallucinationDetails] = useState(false);

    if (!faithfulness_score && !hallucination_risk && !uncertainty_metrics) {
        return null;
    }

    const getScoreColor = (score, inverse = false) => {
        if (inverse) score = 1 - score;
        if (score >= 0.7) return 'text-emerald-600 bg-emerald-50';
        if (score >= 0.4) return 'text-amber-600 bg-amber-50';
        return 'text-red-600 bg-red-50';
    };

    const getScoreIcon = (score, inverse = false) => {
        if (inverse) score = 1 - score;
        if (score >= 0.7) return <CheckCircle className="w-4 h-4" />;
        if (score >= 0.4) return <AlertTriangle className="w-4 h-4" />;
        return <XCircle className="w-4 h-4" />;
    };

    return (
        <div className="space-y-4">
            <h3 className="text-sm font-semibold text-slate-700 flex items-center gap-2">
                <Info className="w-4 h-4 text-indigo-600" />
                Trustworthiness Metrics
            </h3>

            {/* Faithfulness Score */}
            {faithfulness_score !== null && (
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-slate-600">Faithfulness</span>
                        <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold ${getScoreColor(faithfulness_score)}`}>
                            {getScoreIcon(faithfulness_score)}
                            {(faithfulness_score * 100).toFixed(0)}%
                        </div>
                    </div>
                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div
                            className={`h-full transition-all ${faithfulness_score >= 0.7 ? 'bg-emerald-500' : faithfulness_score >= 0.4 ? 'bg-amber-500' : 'bg-red-500'}`}
                            style={{ width: `${faithfulness_score * 100}%` }}
                        />
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                        {faithfulness_reasoning?.interpretation || 'Measures if answer is grounded in source documents'}
                    </p>

                    {/* Reasoning Details Toggle */}
                    {faithfulness_reasoning?.reasoning && faithfulness_reasoning.reasoning.length > 0 && (
                        <div className="mt-2">
                            <button
                                onClick={() => setShowFaithfulnessDetails(!showFaithfulnessDetails)}
                                className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                            >
                                {showFaithfulnessDetails ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                                {showFaithfulnessDetails ? 'Hide' : 'Show'} reasoning
                            </button>

                            {showFaithfulnessDetails && (
                                <div className="mt-2 space-y-1 bg-white rounded p-2 border border-slate-200">
                                    {faithfulness_reasoning.reasoning.map((reason, idx) => (
                                        <p key={idx} className="text-xs text-slate-600">
                                            • {reason}
                                        </p>
                                    ))}
                                    {faithfulness_reasoning.grounded_sentences !== undefined && (
                                        <p className="text-xs font-medium text-slate-700 mt-2">
                                            Grounded sentences: {faithfulness_reasoning.grounded_sentences}/{faithfulness_reasoning.total_sentences}
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Hallucination Risk */}
            {hallucination_risk !== null && (
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-slate-600">Hallucination Risk</span>
                        <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold ${getScoreColor(hallucination_risk, true)}`}>
                            {getScoreIcon(hallucination_risk, true)}
                            {(hallucination_risk * 100).toFixed(0)}%
                        </div>
                    </div>
                    <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div
                            className={`h-full transition-all ${hallucination_risk <= 0.3 ? 'bg-emerald-500' : hallucination_risk <= 0.6 ? 'bg-amber-500' : 'bg-red-500'}`}
                            style={{ width: `${hallucination_risk * 100}%` }}
                        />
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                        {hallucination_reasoning?.interpretation || 'Risk of unsupported claims in answer'}
                    </p>

                    {/* Hallucination Details Toggle */}
                    {hallucination_reasoning?.issues && hallucination_reasoning.issues.length > 0 && (
                        <div className="mt-2">
                            <button
                                onClick={() => setShowHallucinationDetails(!showHallucinationDetails)}
                                className="text-xs text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                            >
                                {showHallucinationDetails ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                                {showHallucinationDetails ? 'Hide' : 'Show'} details
                            </button>

                            {showHallucinationDetails && (
                                <div className="mt-2 space-y-1 bg-white rounded p-2 border border-slate-200">
                                    {hallucination_reasoning.issues.map((issue, idx) => (
                                        <p key={idx} className="text-xs text-slate-600">
                                            • {issue}
                                        </p>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}


            {/* Uncertainty Metrics */}
            {uncertainty_metrics && (
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-slate-600">Uncertainty</span>
                        <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-semibold ${getScoreColor(uncertainty_metrics.total_uncertainty, true)}`}>
                            {getScoreIcon(uncertainty_metrics.total_uncertainty, true)}
                            {(uncertainty_metrics.total_uncertainty * 100).toFixed(0)}%
                        </div>
                    </div>
                    <div className="space-y-1 mt-2">
                        <div className="flex justify-between text-xs">
                            <span className="text-slate-500">Epistemic (Model):</span>
                            <span className="font-mono text-slate-700">{(uncertainty_metrics.epistemic_uncertainty * 100).toFixed(0)}%</span>
                        </div>
                        <div className="flex justify-between text-xs">
                            <span className="text-slate-500">Aleatoric (Data):</span>
                            <span className="font-mono text-slate-700">{(uncertainty_metrics.aleatoric_uncertainty * 100).toFixed(0)}%</span>
                        </div>
                    </div>
                    <p className="text-xs text-slate-500 mt-2 italic">
                        {uncertainty_metrics.interpretation}
                    </p>
                </div>
            )}

            {/* Quality Gates */}
            {quality_gate_results && (
                <div className="bg-slate-50 rounded-lg p-3">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-slate-600">Quality Gates</span>
                        <div className={`px-2 py-1 rounded text-xs font-semibold ${quality_gate_results.action === 'allow' ? 'bg-emerald-100 text-emerald-700' :
                            quality_gate_results.action === 'flag' ? 'bg-amber-100 text-amber-700' :
                                'bg-red-100 text-red-700'
                            }`}>
                            {quality_gate_results.action.toUpperCase()}
                        </div>
                    </div>
                    <p className="text-xs text-slate-600 mb-2">{quality_gate_results.action_message}</p>

                    <div className="space-y-1">
                        {quality_gate_results.gates.map((gate, idx) => (
                            <div key={idx} className="flex items-center gap-2 text-xs">
                                {gate.passed ?
                                    <CheckCircle className="w-3 h-3 text-emerald-500 flex-shrink-0" /> :
                                    <XCircle className="w-3 h-3 text-red-500 flex-shrink-0" />
                                }
                                <span className={gate.passed ? 'text-slate-600' : 'text-red-600'}>
                                    {gate.gate.replace(/_/g, ' ')}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default TrustworthinessPanel;
