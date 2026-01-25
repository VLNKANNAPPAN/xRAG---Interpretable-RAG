# xRAG - Explainable RAG System

> 🔍 **Interpretable Retrieval-Augmented Generation with Multi-Layer Transparency**

xRAG is a comprehensive RAG (Retrieval-Augmented Generation) system that not only provides accurate answers but also explains *why* and *how* it generated each response, making AI decision-making transparent and trustworthy.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Key Features

### 🎯 Core RAG Functionality
- **Multi-format Document Support**: Upload PDFs, Word docs, text files, and more
- **Semantic Search**: FAISS-powered vector similarity search
- **LLM Integration**: Supports Gemini, Ollama (Llama3), and Hugging Face models

### 🔬 Explainability & Transparency
- **Chunk Attribution**: See exactly which source chunks influenced the answer
- **SHAP-style Analysis**: Visual contribution scores for each source
- **Token-level Attribution**: Understand how each part of the answer was generated
- **TSNE Visualization**: Visualize embedding space with query and retrieved chunks

### ✅ Trustworthiness Metrics
- **Faithfulness Scoring**: Measures how grounded the answer is in sources (semantic similarity-based)
- **Hallucination Detection**: Multi-signal detection of unsupported claims
- **Uncertainty Quantification**: Epistemic and aleatoric uncertainty estimates
- **Quality Gates**: Automatic answer validation with pass/fail criteria

### 📊 Advanced Features
- **Retrieval Quality Metrics**: MRR, MAP, context utilization
- **Counterfactual Explanations**: "What if we removed this chunk?"
- **Confidence Calibration**: Calibrated confidence scores
- **Failure Detection**: Automatic detection of potential issues

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- (Optional) Ollama for local LLM

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/VLNKANNAPPAN/xRAG---Interpretable-RAG-.git
   cd xRAG---Interpretable-RAG-
   ```

2. **Set up Python environment**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Start the backend**
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

6. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```

7. **Open the app** at http://localhost:5173

## 📁 Project Structure

```
xRAG/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── retrieval/           # Document retrieval & embedding
│   ├── generation/          # LLM response generation
│   ├── trustworthiness/     # Faithfulness & hallucination detection
│   └── explainability/      # SHAP, attributions, counterfactuals
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   └── visualizations/  # Charts & embedding viz
│   └── ...
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md
```

## 🔧 Configuration

### LLM Providers

| Provider | Setup Guide | Best For |
|----------|-------------|----------|
| Gemini | [GEMINI_SETUP.md](GEMINI_SETUP.md) | Cloud, high quality |
| Ollama | [OLLAMA_SETUP.md](OLLAMA_SETUP.md) | Local, privacy |
| Hugging Face | [HF_API_SETUP.md](HF_API_SETUP.md) | Open models |

### Environment Variables

See [ENV_SETUP.md](ENV_SETUP.md) for detailed configuration.

## 🧪 How It Works

1. **Document Ingestion**: Upload documents → chunked → embedded → stored in FAISS
2. **Query Processing**: User query → embedded → semantic search → top-k chunks retrieved
3. **Answer Generation**: Chunks + query → LLM → answer with citations
4. **Explainability**: 
   - SHAP values computed for chunk contributions
   - Faithfulness scored via semantic similarity
   - Hallucination detected via claim verification
5. **Quality Assurance**: Answer passes through quality gates before delivery

## 📈 Trustworthiness Dashboard

The system provides real-time trustworthiness metrics:

- **Faithfulness Score**: How well the answer matches source content
- **Hallucination Risk**: Probability of unsupported claims
- **Confidence**: Model's self-assessed certainty
- **Quality Gates**: Pass/flag/reject status

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- FAISS by Facebook Research
- Sentence Transformers
- FastAPI
- React & Plotly
