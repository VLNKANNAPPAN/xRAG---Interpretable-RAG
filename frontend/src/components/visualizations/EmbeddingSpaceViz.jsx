import React from 'react';
import Plot from 'react-plotly.js';

const EmbeddingSpaceViz = ({ vizData }) => {
    if (!vizData || !vizData.points) {
        return (
            <div className="bg-slate-50 rounded-lg p-4 text-center text-slate-500">
                <p>No embedding visualization data available</p>
            </div>
        );
    }

    const { points, n_components } = vizData;

    // Separate query and chunk points
    const queryPoints = points.filter(p => p.type === 'query');
    const retrievedChunks = points.filter(p => p.type === 'chunk' && p.retrieved);
    const nonRetrievedChunks = points.filter(p => p.type === 'chunk' && !p.retrieved);

    const createTrace = (data, name, color, symbol = 'circle') => ({
        x: data.map(p => p.x),
        y: data.map(p => p.y),
        z: n_components === 3 ? data.map(p => p.z) : undefined,
        mode: 'markers',
        type: n_components === 3 ? 'scatter3d' : 'scatter',
        name: name,
        marker: {
            size: name === 'Query' ? 18 : (name === 'Retrieved Chunks' ? 14 : 6),  // Retrieved chunks are bigger
            color: color,
            symbol: symbol,
            opacity: name === 'Other Chunks' ? 0.4 : 1.0,  // Non-retrieved are faded
            line: {
                color: name === 'Query' ? '#fff' : (name === 'Retrieved Chunks' ? '#065f46' : undefined),
                width: name === 'Query' ? 2 : (name === 'Retrieved Chunks' ? 2 : 0)
            }
        },
        text: data.map(p => p.text || p.label),
        hovertemplate: '<b>%{text}</b><br>x: %{x:.2f}<br>y: %{y:.2f}' +
            (n_components === 3 ? '<br>z: %{z:.2f}' : '') +
            '<extra></extra>'
    });

    const traces = [
        createTrace(queryPoints, 'Query', '#6366f1', 'star'),
        createTrace(retrievedChunks, 'Retrieved Chunks', '#10b981', 'circle'),  // Bright green
        createTrace(nonRetrievedChunks, 'Other Chunks', '#cbd5e1', 'circle')    // Faded gray
    ];

    const layout = {
        title: {
            text: `Embedding Space (${vizData.method.toUpperCase()})`,
            font: { size: 14, color: '#334155' }
        },
        showlegend: true,
        legend: {
            x: 1,
            xanchor: 'right',
            y: 1
        },
        hovermode: 'closest',
        margin: { l: 0, r: 0, t: 40, b: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: {
            showgrid: true,
            gridcolor: '#e2e8f0',
            zeroline: false
        },
        yaxis: {
            showgrid: true,
            gridcolor: '#e2e8f0',
            zeroline: false
        },
        ...(n_components === 3 && {
            scene: {
                xaxis: { showgrid: true, gridcolor: '#e2e8f0' },
                yaxis: { showgrid: true, gridcolor: '#e2e8f0' },
                zaxis: { showgrid: true, gridcolor: '#e2e8f0' }
            }
        })
    };

    return (
        <div className="bg-white rounded-lg p-4 border border-slate-200">
            <Plot
                data={traces}
                layout={layout}
                config={{
                    responsive: true,
                    displayModeBar: true,
                    displaylogo: false,
                    modeBarButtonsToRemove: ['lasso2d', 'select2d']
                }}
                style={{ width: '100%', height: '400px' }}
            />
            <div className="mt-2 text-xs text-slate-500">
                <p>Showing {vizData.num_retrieved} retrieved out of {vizData.num_chunks} total chunks</p>
            </div>
        </div>
    );
};

export default EmbeddingSpaceViz;
