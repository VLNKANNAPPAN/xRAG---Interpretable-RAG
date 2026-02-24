<div align="center">

# 🧠 xRAG - Explainable & Trustworthy RAG System

> **Transparent, Reliable, and Interpretable Retrieval-Augmented Generation**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

xRAG is an open-source, full-stack application that transforms traditional 'black-box' Retrieval-Augmented Generation (RAG) into a highly interpretable and accountable process. It doesn't just give you an answer; it tells you exactly **why**, **how confident** it is, and **whether it's hallucinating**!

[Features](#-key-features) • [Installation](#-quick-start) • [How it Works](#-how-it-works) • [Dashboard](#-trustworthiness-dashboard) • [Deployment](#-deployment)

---

</div>

## ✨ Key Features

### 🎯 Core RAG Functionality
- **Multi-format Document Ingestion**: Seamlessly upload and process PDFs, Word docs, texts, and more.
- **Semantic Vector Search**: High-performance similarity search powered by [FAISS](https://github.com/facebookresearch/faiss).
- **Flexible LLM Integration**: Natively supports [Groq](https://groq.com) (Llama-3), Gemini, Ollama, and Hugging Face.

### 🔬 Explainability & Transparency
- **Chunk-Level Attribution**: Visualized source mapping showing exactly which retrieved document chunks influenced the final answer.
- **SHAP-Style Analytics**: Visual contribution scoring quantifying the exact impact of each source.
- **Token-Level Attribution**: Fine-grained highlighting indicating how each sentence in the answer corresponds to retrieved data.
- **T-SNE Visualization**: Interactive 2D mapping of your documents' vector embedding space alongside user queries.

### ✅ Trustworthiness & Reliability Metrics
- **Faithfulness Scoring**: Deep semantic analysis to ensure the answer is strictly grounded in the provided sources.
- **Hallucination Detection**: Multi-signal detection engine that identifies unsupported claims, entity mismatches, and contradictory numbers.
- **Uncertainty Quantification**: Calculates dynamic *epistemic* and *aleatoric* uncertainty.
- **Quality Gates**: Automated rules-engine preventing poor-quality or hallucinated responses from reaching the user.

## 🚀 Quick Start

Follow these steps to clone, configure, and run **xRAG** on your local machine.

### Prerequisites
Before you start, ensure you have the following installed on your system:
- **Git**
- **Python 3.10+** (Required for the backend machinery)
- **Node.js 18+** & **npm** (Required for the React frontend)
- A **Groq API Key** (Free tier available at [console.groq.com](https://console.groq.com))

### 1️⃣ Clone the Repository

Clone this project to your computer and navigate into the directory:

```bash
git clone https://github.com/VLNKANNAPPAN/xRAG---Interpretable-RAG-.git
cd xRAG---Interpretable-RAG-
```

### 2️⃣ Backend Setup (FastAPI + Data Science Stack)

Open a new terminal to configure the Python backend:

```bash
# Optional: Create and activate a virtual environment
# python -m venv venv
# source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install the required Python dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables
Copy the example environment variables file and add your API keys:

```bash
cp .env.example .env
```
Open the newly created `.env` file in a text editor and update it with your actual keys (e.g., set your `GROQ_API_KEY`).

#### Start the Backend Server
Once setup is complete, start the FastAPI application:

```bash
python -m uvicorn backend.main:app --reload
```
*The backend should now be running on `http://localhost:8000`.*

### 3️⃣ Frontend Setup (React + Vite)

Open a **separate, new terminal window** (keep the backend running in the first one), and configure the frontend:

```bash
# Navigate to the frontend directory
cd frontend

# Install Node modules and dependencies
npm install

# Start the Vite development server
npm run dev
```

### 4️⃣ Use the Application
🎉 **You're all set!** Open your browser and navigate to:
**http://localhost:5173**

You can now start uploading documents and querying the system!

---

## 📁 Project Structure

```text
xRAG/
├── backend/
│   ├── main.py              # FastAPI application & endpoints
│   ├── retrieval/           # FAISS index, embedding, reranker
│   ├── generation/          # LLM prompt construction & responses
│   ├── trustworthiness/     # Hallucination, faithfulness, calibration
│   └── explainability/      # SHAP values, attributions, T-SNE
├── frontend/
│   ├── src/
│   │   ├── components/      # React components (Upload, Chat, Dashboard)
│   │   └── visualizations/  # Plotly & D3 Charts 
├── uploaded_files/          # Temporary storage for ingested docs
├── .env.example             # Environment configs template
├── requirements.txt         # Python dependencies
└── README.md
```

## 🧪 How It Works

1. **Ingestion**: Uploaded documents are parsed, chunked into smaller segments, and embedded using `sentence-transformers`. The resulting vectors are stored persistently in a local FAISS index alongside metadata in SQLite.
2. **Retrieval**: When a query is asked, the system embeds the text and performs an optimized semantic search on the vector database to find the top-$k$ most relevant chunks.
3. **Generation**: The retrieved chunks and the user query are injected into a highly crafted prompt and sent to an LLM (e.g., Groq's Llama-3).
4. **Analysis Pipeline**:
    - Calculates SHAP similarity contributions.
    - Evaluates structural faithfulness and specific entity/fact adherence.
    - Calibrates confidence metrics and tests threshold Quality Gates.
5. **Dashboard Rendering**: The React frontend compiles the complex JSON metadata into interactive visualizations.

## 📈 Trustworthiness Dashboard

Unlike traditional chatbots, xRAG gives you an auxiliary dashboard for every single answer explaining its origin:
- **Overall Confidence Meter**: Blends retrieval quality, certainty, and hallucination absence.
- **Source Contribution Chart**: A horizontal bar chart identifying how much weight each document excerpt held.
- **Risk Assessment Panel**: Clearly states identified risk factors like "Potential Entity Hallucination" or "Number Mismatches."

## ☁️ Deployment

Planning to take this live? xRAG is architected to be deployed across cloud providers.
Please see our detailed [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions on deploying the frontend to **Vercel** and the heavy ML backend to **Render**.

## 🤝 Contributing

Contributions are heavily encouraged! If you're passionate about making LLMs safe, interpretable, and accountable, please:
1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## 🙏 Acknowledgments

- [FAISS](https://github.com/facebookresearch/faiss) by Facebook Research for blazing-fast vector search.
- Setting up the ML backend requires heavy-lifting thanks to [PyTorch](https://pytorch.org/) & [SentenceTransformers](https://sbert.net/).
- Inspired by modern XAI (Explainable AI) methodologies!
