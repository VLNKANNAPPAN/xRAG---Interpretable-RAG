from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import uuid
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from backend.retrieval.retriever import retrieve
from backend.retrieval.metrics import calculate_retrieval_metrics
from backend.retrieval.reranker import rerank_chunks
from backend.retrieval.embedding_visualizer import create_quick_2d_visualization
from backend.explainability.shap_attribution import shap_attribution
from backend.explainability.counterfactual import generate_counterfactual_explanations
from backend.explainability.token_attribution import calculate_token_attribution
from backend.failure.failure_detector import detect_failures
from backend.failure.refusal import should_refuse
from backend.trustworthiness.enhanced_faithfulness import enhanced_faithfulness_score
from backend.trustworthiness.enhanced_hallucination import enhanced_hallucination_detection
from backend.validation.answer_validator import validate_answer
from backend.trustworthiness.calibration import calibrate_confidence, calculate_ece
from backend.trustworthiness.uncertainty import quantify_uncertainty
from backend.evaluation.quality_gates import check_quality_gates, get_quality_recommendations
from backend.embeddings.embedder import embed_texts
from backend.embeddings.vector_store import update_index, load_index, clear_index
from backend.ingestion.loader import load_document
from backend.ingestion.chunker import chunk_documents
from backend.database import init_db, save_document_metadata, get_all_chunks, get_all_documents, clear_db, get_chunk_text

# Initialize DB
init_db()

# -----------------------------
# App setup
# -----------------------------
app = FastAPI(title="Explainable Failure-Aware RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# -----------------------------
# Request / Response schemas
# -----------------------------
class QueryRequest(BaseModel):
    query: str

class ChunkInfo(BaseModel):
    text: str
    shap_score: float
    similarity_score: float
    page: int | None
    source: str

class QueryResponse(BaseModel):
    # Basic response
    answer: str | None
    refused: bool
    refusal_reasons: list[str]
    
    # Confidence metrics
    confidence: float
    calibrated_confidence: float | None = None
    
    # Attribution
    shap: list[tuple[str, float]]
    top_chunks: list[ChunkInfo]
    source_documents: list[str]
    
    # Trustworthiness metrics
    faithfulness_score: float | None = None
    faithfulness_reasoning: dict | None = None  # NEW: Detailed reasoning
    hallucination_risk: float | None = None
    hallucination_reasoning: dict | None = None  # NEW: Detailed reasoning
    uncertainty_metrics: dict | None = None
    
    # Retrieval metrics
    retrieval_metrics: dict | None = None
    embedding_viz_data: dict | None = None
    
    # Advanced explainability
    token_attributions: dict | None = None
    counterfactual_explanations: dict | None = None
    
    # Quality gates
    quality_gate_results: dict | None = None
    
    # Warnings and recommendations
    warnings: list[str]
    recommendations: list[str] = []

class DocumentResponse(BaseModel):
    id: str
    filename: str
    num_chunks: int

# -----------------------------
# API Endpoints
# -----------------------------

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    new_chunks_text = []
    
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            doc_data = load_document(file_path)
        except Exception as e:
             raise HTTPException(status_code=400, detail=f"Error parsing {file.filename}: {str(e)}")
             
        # Use improved chunker
        chunks, metadatas = chunk_documents(doc_data["segments"])
        
        if not chunks:
             continue
             
        doc_id = str(uuid.uuid4())
        save_document_metadata(doc_id, doc_data["filename"], doc_data["content"], chunks, metadatas)
        new_chunks_text.extend(chunks)

    if new_chunks_text:
        update_index(new_chunks_text)
        
    return {"message": f"Successfully processed {len(files)} files."}

@app.get("/documents", response_model=List[DocumentResponse])
def list_documents():
    return get_all_documents()

@app.delete("/reset")
def reset_knowledge_base():
    clear_db()
    clear_index()
    # clean upload dir
    for f in os.listdir(UPLOAD_DIR):
        os.remove(os.path.join(UPLOAD_DIR, f))
    return {"message": "Knowledge base reset."}

@app.post("/query", response_model=QueryResponse)
def query_rag(req: QueryRequest):
    index = load_index()
    
    if index is None or index.ntotal == 0:
        return QueryResponse(
            answer=None,
            refused=True,
            refusal_reasons=["Knowledge base is empty."],
            confidence=0.0,
            shap=[],
            warnings=["No documents uploaded."],
            source_documents=[]
        )

    # -----------------------------
    # Retrieve relevant chunks
    # -----------------------------
    all_chunks_data = get_all_chunks() 
    
    # Map text -> metadata keys to easily find metadata after retrieval
    # (Note: In a real system, we would track IDs properly. Here relying on text match implies uniqueness assumption)
    text_to_meta = {c["text"]: c.get("metadata", {}) for c in all_chunks_data}
    text_to_docid = {c["text"]: c.get("doc_id", "") for c in all_chunks_data}
    
    # Get filenames map
    doc_id_map = {d["id"]: d["filename"] for d in get_all_documents()}

    all_texts = [c["text"] for c in all_chunks_data]
    
    retrieved = retrieve(req.query, index, all_texts)
    
    chunks = [r["text"] for r in retrieved]
    similarities = [float(r["similarity"]) for r in retrieved]

    # -----------------------------
    # Explainable RAG (SHAP)
    # -----------------------------
    answer, shap = shap_attribution(
        req.query,
        chunks,
        similarities
    )

    shap_scores = [score for _, score in shap]
    
    # -----------------------------
    # Trustworthiness Validation (ENHANCED)
    # -----------------------------
    
    # Step 1: Validate answer before scoring
    validation_result = validate_answer(answer, chunks, req.query)
    
    if not validation_result or not validation_result["valid"]:
        # Answer failed validation - refuse
        return QueryResponse(
            answer=None,
            refused=True,
            refusal_reasons=[validation_result["reason"] if validation_result else "Answer validation failed"],
            confidence=0.0,
            shap=[],
            warnings=["Answer did not pass validation checks"],
            source_documents=[],
            top_chunks=[]  # Add missing field
        )
    
    # Use validated (potentially filtered) answer
    validated_answer = validation_result["answer"]
    
    # Step 2: Enhanced faithfulness scoring (semantic-based)
    faithfulness_result = enhanced_faithfulness_score(validated_answer, chunks)
    faithfulness_score = faithfulness_result["overall_score"]
    
    # Extract faithfulness reasoning with clear explanations
    faithfulness_reasoning = {
        "interpretation": faithfulness_result.get("interpretation", ""),
        "semantic_score": faithfulness_result.get("semantic_score", 0),  # PRIMARY
        "sentence_score": faithfulness_result.get("sentence_score", 0),
        "fact_score": faithfulness_result.get("fact_score", 0),
        "nli_score": faithfulness_result.get("nli_score", 0),
        "reasoning": faithfulness_result.get("reasoning", []),  # NEW: Clear explanations
        "sentence_analysis": faithfulness_result.get("sentence_analysis", []),
        "fact_details": faithfulness_result.get("fact_details", {}),
        "semantic_details": faithfulness_result.get("semantic_details", {}),
        "grounded_sentences": faithfulness_result.get("grounded_sentences", 0),
        "total_sentences": faithfulness_result.get("total_sentences", 0)
    }
    
    # Step 3: Enhanced hallucination detection (multi-signal)
    hallucination_result = enhanced_hallucination_detection(validated_answer, chunks)
    hallucination_risk = hallucination_result["overall_risk"]
    
    # Extract hallucination reasoning with sentence-level detail
    hallucination_reasoning = {
        "interpretation": hallucination_result.get("interpretation", ""),
        "entity_risk": hallucination_result.get("entity_risk", 0),
        "number_risk": hallucination_result.get("number_risk", 0),
        "claim_risk": hallucination_result.get("claim_risk", 0),
        "contradiction_risk": hallucination_result.get("contradiction_risk", 0),
        "issues": [],
        "sentence_analysis": hallucination_result.get("sentence_analysis", []),  # NEW
        "entity_details": hallucination_result.get("entity_details", {}),  # NEW
        "number_details": hallucination_result.get("number_details", {}),  # NEW
        "high_risk_sentences": hallucination_result.get("high_risk_sentences", 0),
        "total_sentences": hallucination_result.get("total_sentences", 0)
    }
    
    if hallucination_result.get("entity_risk", 0) > 0.3:
        hallucination_reasoning["issues"].append(f"Named entities not found in sources (risk: {hallucination_result.get('entity_risk', 0):.0%})")
    if hallucination_result.get("number_risk", 0) > 0.3:
        hallucination_reasoning["issues"].append(f"Numbers not verified in sources (risk: {hallucination_result.get('number_risk', 0):.0%})")
    if hallucination_result.get("claim_risk", 0) > 0.4:
        hallucination_reasoning["issues"].append(f"Some claims not supported by sources (risk: {hallucination_result.get('claim_risk', 0):.0%})")
    if hallucination_result.get("contradiction_risk", 0) > 0.3:
        hallucination_reasoning["issues"].append(f"Potential contradiction with sources (risk: {hallucination_result.get('contradiction_risk', 0):.0%})")
    
    # Step 4: Uncertainty quantification (reduced to 1 sample to avoid API rate limits)
    try:
        uncertainty_metrics = quantify_uncertainty(
            req.query,
            chunks,
            num_samples=1,  # Reduced from 3 to save API calls
            shap_scores=shap_scores
        )
    except Exception as e:
        print(f"Warning: Uncertainty quantification failed: {e}")
        uncertainty_metrics = {
            "total_uncertainty": 0.5,
            "epistemic_uncertainty": 0.5,
            "aleatoric_uncertainty": 0.5,
            "interpretation": "Uncertainty quantification unavailable"
        }
    
    # -----------------------------
    # Retrieval Metrics
    # -----------------------------
    retrieval_metrics = calculate_retrieval_metrics(
        req.query,
        chunks,
        similarities
    )
    
    # -----------------------------
    # Advanced Explainability
    # -----------------------------
    # Token-level attribution
    token_attributions = calculate_token_attribution(
        answer,
        chunks,
        shap_scores
    )
    
    # Counterfactual explanations (limit to top 2 chunks to save API calls)
    # Set ENABLE_COUNTERFACTUAL=False to skip this expensive feature
    ENABLE_COUNTERFACTUAL = False  # Disable by default to save API quota
    
    if ENABLE_COUNTERFACTUAL:
        try:
            counterfactual_explanations = generate_counterfactual_explanations(
                req.query,
                chunks,
                base_answer=answer,
                max_chunks_to_test=min(2, len(chunks))  # Reduced from 3 to 2
            )
        except Exception as e:
            print(f"Warning: Counterfactual generation failed: {e}")
            counterfactual_explanations = None
    else:
        counterfactual_explanations = None
    
    # -----------------------------
    # Embedding Visualization
    # -----------------------------
    try:
        # Get embeddings for visualization
        query_emb = embed_texts([req.query])[0]
        chunk_embs = embed_texts(all_texts)
        
        # Fix: Properly find indices of retrieved chunks
        retrieved_indices = []
        for chunk in chunks:
            # Try exact match first
            if chunk in all_texts:
                idx = all_texts.index(chunk)
                if idx not in retrieved_indices:
                    retrieved_indices.append(idx)
            else:
                # Fallback: find best matching chunk by content overlap
                for i, text in enumerate(all_texts):
                    if text[:100] == chunk[:100] or text in chunk or chunk in text:
                        if i not in retrieved_indices:
                            retrieved_indices.append(i)
                            break
        
        print(f"TSNE: Found {len(retrieved_indices)} retrieved chunks out of {len(all_texts)} total")  # Debug
        
        embedding_viz_data = create_quick_2d_visualization(
            query_emb,
            chunk_embs,
            retrieved_indices,
            chunk_texts=all_texts
        )
    except Exception as e:
        print(f"Error creating embedding visualization: {e}")
        import traceback
        traceback.print_exc()
        embedding_viz_data = None

    # -----------------------------
    # Failure detection
    # -----------------------------
    failure_report = detect_failures(
        similarities,
        shap_scores
    )
    
    # Calibrate confidence
    raw_confidence = failure_report["confidence"]
    calibrated_conf = calibrate_confidence(raw_confidence)
    
    # -----------------------------
    # Quality Gates
    # -----------------------------
    quality_gate_results = check_quality_gates(
        faithfulness_score=faithfulness_score,
        hallucination_risk=hallucination_risk,
        confidence=raw_confidence,
        calibrated_confidence=calibrated_conf,
        max_similarity=max(similarities) if similarities else 0.0
    )
    
    recommendations = get_quality_recommendations(quality_gate_results)
    
    # -----------------------------
    # Construct Rich Metadata Response
    # -----------------------------
    top_chunks = []
    # Map shap scores back to chunks. shap returns [(chunk_text, score)]
    # We also have 'similarities' list which corresponds to 'chunks' list
    
    # Create a map for quick lookup if needed, but lists are aligned
    shap_map = {text: score for text, score in shap}
    
    for i, chunk_text in enumerate(chunks):
        meta = text_to_meta.get(chunk_text, {})
        doc_id = text_to_docid.get(chunk_text, "")
        filename = doc_id_map.get(doc_id, "Unknown")
        
        top_chunks.append(ChunkInfo(
            text=chunk_text,
            shap_score=shap_map.get(chunk_text, 0.0),
            similarity_score=similarities[i],
            page=meta.get("page"),
            source=filename
        ))
        
    # Sort by SHAP score descending
    top_chunks.sort(key=lambda x: x.shap_score, reverse=True)

    response = {
        "answer": validated_answer,  # Use validated answer instead of raw answer
        "shap": shap,
        "confidence": raw_confidence,
        "calibrated_confidence": calibrated_conf,
        "warnings": failure_report["warnings"],
        "faithfulness_score": faithfulness_score,
        "faithfulness_details": faithfulness_result,  # Include detailed breakdown
        "faithfulness_reasoning": faithfulness_reasoning,  # NEW: User-friendly reasoning
        "hallucination_risk": hallucination_risk,
        "hallucination_details": hallucination_result,  # Include detailed breakdown
        "hallucination_reasoning": hallucination_reasoning,  # NEW: User-friendly reasoning
        "uncertainty_metrics": uncertainty_metrics,
        "retrieval_metrics": retrieval_metrics,
        "token_attributions": token_attributions,
        "counterfactual_explanations": counterfactual_explanations,
        "embedding_viz_data": embedding_viz_data,
        "quality_gate_results": quality_gate_results,
        "recommendations": recommendations,
        "validation_info": {
            "was_filtered": validation_result.get("filtered", False),
            "original_answer": validation_result.get("original_answer") if validation_result.get("filtered") else None
        }
    }

    # -----------------------------
    # Refusal logic
    # -----------------------------
    refusal = should_refuse(response)

    if refusal["refuse"] or quality_gate_results["action"] == "reject":
        # Combine refusal reasons with quality gate issues
        all_refusal_reasons = refusal["reasons"].copy()
        if quality_gate_results["action"] == "reject":
            all_refusal_reasons.append(quality_gate_results["action_message"])
        
        return QueryResponse(
            answer=None,
            refused=True,
            refusal_reasons=all_refusal_reasons,
            confidence=response["confidence"],
            calibrated_confidence=response["calibrated_confidence"],
            shap=response["shap"],
            top_chunks=top_chunks,
            warnings=response["warnings"],
            recommendations=response["recommendations"],
            source_documents=[],
            faithfulness_score=response["faithfulness_score"],
            hallucination_risk=response["hallucination_risk"],
            uncertainty_metrics=response["uncertainty_metrics"],
            retrieval_metrics=response["retrieval_metrics"],
            quality_gate_results=response["quality_gate_results"]
        )

    return QueryResponse(
        answer=answer,
        refused=False,
        refusal_reasons=[],
        confidence=response["confidence"],
        calibrated_confidence=response["calibrated_confidence"],
        shap=response["shap"],
        top_chunks=top_chunks,
        warnings=response["warnings"],
        recommendations=response["recommendations"],
        source_documents=list(set(chunks)),
        faithfulness_score=response["faithfulness_score"],
        faithfulness_reasoning=response["faithfulness_reasoning"],  # NEW
        hallucination_risk=response["hallucination_risk"],
        hallucination_reasoning=response["hallucination_reasoning"],  # NEW
        uncertainty_metrics=response["uncertainty_metrics"],
        retrieval_metrics=response["retrieval_metrics"],
        token_attributions=response["token_attributions"],
        counterfactual_explanations=response["counterfactual_explanations"],
        embedding_viz_data=response["embedding_viz_data"],
        quality_gate_results=response["quality_gate_results"]
    )
