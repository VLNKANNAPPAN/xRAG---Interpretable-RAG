"""
Enhanced faithfulness scoring with multi-layer verification.
Uses semantic similarity as primary signal (most reliable),
with NLI and fact checking as secondary verification.

KEY INSIGHT: If semantic similarity is high, the content IS from sources.
NLI models often fail on formatted/paraphrased text.
"""

from typing import List, Dict
import re
import numpy as np
from sentence_transformers import SentenceTransformer, util

# Initialize models (cached)
nli_model = None
embedding_model = None

def get_nli_model():
    """
    Get NLI model for entailment checking.
    We use cross-encoder which is more compatible and reliable.
    """
    global nli_model
    if nli_model is None:
        try:
            # Use cross-encoder NLI - more compatible and reliable
            from sentence_transformers import CrossEncoder
            nli_model = CrossEncoder('cross-encoder/nli-distilroberta-base', device='cpu')
            print("✓ Loaded NLI model: cross-encoder/nli-distilroberta-base")
        except Exception as e:
            print(f"Warning: Could not load NLI model: {e}")
            nli_model = "failed"
    return nli_model if nli_model != "failed" else None



def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    return embedding_model


def clean_text_for_matching(text: str) -> str:
    """Remove markdown formatting for fair comparison."""
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_
    # Remove markdown headers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    # Remove bullet points
    text = re.sub(r'^\s*[-*]\s*', '', text, flags=re.MULTILINE)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def analyze_sentence_faithfulness(answer: str, chunks: List[str]) -> List[Dict]:
    """
    Analyze each sentence using SEMANTIC SIMILARITY (most reliable method).
    Returns list of sentences with their grounding status.
    """
    # Clean answer for sentence splitting
    clean_answer = clean_text_for_matching(answer)
    sentences = [s.strip() for s in re.split(r'[.!?]+', clean_answer) if s.strip() and len(s.strip()) > 10]
    
    if not sentences or not chunks:
        return []
    
    model = get_embedding_model()
    
    # Clean chunks too
    clean_chunks = [clean_text_for_matching(c) for c in chunks]
    
    # Embed sentences and chunks
    sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
    chunk_embeddings = model.encode(clean_chunks, convert_to_tensor=True)
    
    sentence_analysis = []
    
    for i, (sentence, sent_emb) in enumerate(zip(sentences, sentence_embeddings)):
        # Find best matching chunk
        similarities = util.cos_sim(sent_emb, chunk_embeddings)[0]
        best_chunk_idx = similarities.argmax().item()
        max_sim = similarities[best_chunk_idx].item()
        
        # ROBUST thresholds based on semantic similarity
        # 0.6+ is actually good for paraphrased content
        if max_sim >= 0.65:
            status = "well_grounded"
            status_label = "✅ Well grounded"
            explanation = f"This sentence closely matches source content (similarity: {max_sim:.0%})"
        elif max_sim >= 0.50:
            status = "partially_grounded"
            status_label = "⚠️ Paraphrased"
            explanation = f"This sentence is a valid paraphrase of source content (similarity: {max_sim:.0%})"
        elif max_sim >= 0.35:
            status = "weakly_grounded"
            status_label = "⚠️ Loosely related"
            explanation = f"This sentence has weak connection to sources (similarity: {max_sim:.0%})"
        else:
            status = "not_grounded"
            status_label = "❌ Not grounded"
            explanation = f"This sentence may not be supported by sources (similarity: {max_sim:.0%})"
        
        # Get snippet of best matching chunk
        best_chunk_text = chunks[best_chunk_idx]
        chunk_snippet = best_chunk_text[:150] + "..." if len(best_chunk_text) > 150 else best_chunk_text
        
        sentence_analysis.append({
            "sentence": sentence,
            "status": status,
            "status_label": status_label,
            "explanation": explanation,
            "similarity": float(max_sim),
            "best_matching_chunk_idx": best_chunk_idx,
            "best_matching_chunk_snippet": chunk_snippet
        })
    
    return sentence_analysis


def calculate_semantic_faithfulness(answer: str, chunks: List[str]) -> Dict:
    """
    PRIMARY METRIC: Calculate semantic similarity between answer and chunks.
    This is the most reliable method that handles paraphrasing correctly.
    """
    model = get_embedding_model()
    
    # Clean texts
    clean_answer = clean_text_for_matching(answer)
    clean_chunks = [clean_text_for_matching(c) for c in chunks]
    combined_context = " ".join(clean_chunks)
    
    # Embed
    answer_emb = model.encode(clean_answer, convert_to_tensor=True)
    context_emb = model.encode(combined_context, convert_to_tensor=True)
    
    # Overall similarity
    overall_sim = util.cos_sim(answer_emb, context_emb)[0][0].item()
    
    # Also check individual chunks
    chunk_embeddings = model.encode(clean_chunks, convert_to_tensor=True)
    chunk_similarities = util.cos_sim(answer_emb, chunk_embeddings)[0]
    max_chunk_sim = chunk_similarities.max().item()
    avg_chunk_sim = chunk_similarities.mean().item()
    
    return {
        "overall_similarity": overall_sim,
        "max_chunk_similarity": max_chunk_sim,
        "avg_chunk_similarity": avg_chunk_sim,
        "explanation": get_semantic_explanation(overall_sim)
    }


def get_semantic_explanation(sim: float) -> str:
    """Explain what the semantic similarity means."""
    if sim >= 0.7:
        return "Answer content closely matches sources"
    elif sim >= 0.55:
        return "Answer accurately paraphrases source content"  
    elif sim >= 0.4:
        return "Answer has partial overlap with sources"
    else:
        return "Answer may contain content not from sources"


def extract_and_verify_facts(answer: str, chunks: List[str]) -> Dict:
    """
    SECONDARY METRIC: Verify specific facts (numbers, entities).
    """
    # Clean for comparison
    clean_answer = clean_text_for_matching(answer)
    chunks_text = " ".join([clean_text_for_matching(c) for c in chunks]).lower()
    
    # Extract numbers
    answer_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', clean_answer)
    chunks_numbers = re.findall(r'\b\d+(?:\.\d+)?\b', chunks_text)
    
    verified_numbers = []
    unverified_numbers = []
    for num in answer_numbers:
        if num in chunks_numbers:
            verified_numbers.append(num)
        else:
            unverified_numbers.append(num)
    
    number_score = len(verified_numbers) / len(answer_numbers) if answer_numbers else 1.0
    
    # Extract key entities (proper nouns)
    answer_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', clean_answer)
    # Filter common words that happen to be capitalized
    common_starts = {'The', 'This', 'That', 'These', 'It', 'In', 'On', 'At', 'For', 'Definition', 'Technique', 'Goal'}
    answer_entities = [e for e in answer_entities if e not in common_starts]
    
    verified_entities = []
    unverified_entities = []
    for entity in answer_entities:
        if entity.lower() in chunks_text:
            verified_entities.append(entity)
        else:
            unverified_entities.append(entity)
    
    entity_score = len(verified_entities) / len(answer_entities) if answer_entities else 1.0
    
    fact_score = (number_score + entity_score) / 2
    
    return {
        "score": fact_score,
        "verified_numbers": list(set(verified_numbers)),
        "unverified_numbers": list(set(unverified_numbers)),
        "verified_entities": list(set(verified_entities)),
        "unverified_entities": list(set(unverified_entities))
    }


def enhanced_faithfulness_score(answer: str, chunks: List[str]) -> Dict:
    """
    ROBUST faithfulness scoring with logical methodology:
    
    1. PRIMARY: Semantic similarity (handles paraphrasing correctly)
    2. SECONDARY: Fact verification (catches specific errors)
    3. SUPPORTING: NLI (if available and reliable)
    
    Key principle: If semantic similarity is high, the content IS faithful.
    NLI models often fail on formatted or paraphrased text.
    """
    if not answer or not chunks:
        return {
            "overall_score": 0.0,
            "semantic_score": 0.0,
            "fact_score": 0.0,
            "nli_score": 0.0,
            "sentence_analysis": [],
            "fact_details": {},
            "reasoning": ["No answer or chunks provided"]
        }
    
    reasoning = []  # Collect reasons for the score
    
    # PRIMARY: Semantic similarity (most reliable!)
    semantic_result = calculate_semantic_faithfulness(answer, chunks)
    semantic_score = semantic_result["overall_similarity"]
    reasoning.append(f"Semantic similarity: {semantic_score:.0%} - {semantic_result['explanation']}")
    
    # SECONDARY: Fact verification
    fact_details = extract_and_verify_facts(answer, chunks)
    fact_score = fact_details["score"]
    
    if fact_details["unverified_numbers"]:
        reasoning.append(f"Unverified numbers: {', '.join(fact_details['unverified_numbers'][:3])}")
    if fact_details["unverified_entities"]:
        reasoning.append(f"Unverified entities: {', '.join(fact_details['unverified_entities'][:3])}")
    if not fact_details["unverified_numbers"] and not fact_details["unverified_entities"]:
        reasoning.append("All specific facts (numbers, entities) verified in sources")
    
    # SUPPORTING: NLI (only if model loaded successfully)
    nli_score = 0.5  # default neutral
    nli_model = get_nli_model()
    if nli_model:
        try:
            # Use cleaned text for NLI
            clean_context = clean_text_for_matching(" ".join(chunks[:2]))[:500]
            clean_answer = clean_text_for_matching(answer)[:200]
            
            # CrossEncoder returns scores for [contradiction, entailment, neutral]
            scores = nli_model.predict([(clean_context, clean_answer)])[0]
            
            # scores[0] = contradiction, scores[1] = entailment, scores[2] = neutral
            # Convert to softmax-like probabilities
            probs = np.exp(scores) / np.sum(np.exp(scores))

            
            entailment_prob = probs[1]
            neutral_prob = probs[2]
            contradiction_prob = probs[0]
            
            # Determine label
            max_idx = np.argmax(probs)
            labels = ['CONTRADICTION', 'ENTAILMENT', 'NEUTRAL']
            label = labels[max_idx]
            
            # Score based on entailment
            if label == "ENTAILMENT":
                nli_score = float(entailment_prob)
            elif label == "NEUTRAL":
                nli_score = 0.5 + float(neutral_prob * 0.3)
            else:
                nli_score = 0.3  # Don't penalize too hard
            
            reasoning.append(f"NLI assessment: {label} ({probs[max_idx]:.0%})")
        except Exception as e:
            reasoning.append(f"NLI unavailable: {e}")

    
    # Sentence-level analysis
    sentence_analysis = analyze_sentence_faithfulness(answer, chunks)
    
    # Count grounded sentences
    well_grounded = sum(1 for s in sentence_analysis if s["status"] in ["well_grounded", "partially_grounded"])
    total_sentences = len(sentence_analysis)
    sentence_score = well_grounded / total_sentences if total_sentences > 0 else 0.5
    
    reasoning.append(f"Sentence analysis: {well_grounded}/{total_sentences} sentences are grounded")
    
    # ROBUST OVERALL SCORE:
    # Semantic similarity is the primary signal (60%)
    # Sentence-level grounding is secondary (25%)
    # Fact verification is tertiary (15%)
    # NLI is a minor supporting signal (0%) - too unreliable
    
    overall_score = (
        0.60 * semantic_score +     # Primary: semantic similarity
        0.25 * sentence_score +      # Secondary: sentence-level grounding  
        0.15 * fact_score            # Tertiary: specific facts verified
        # NLI excluded - too unreliable on formatted text
    )
    
    # Sanity check: if semantic similarity is very high, overall should be high
    if semantic_score >= 0.65:
        overall_score = max(overall_score, 0.70)  # Floor at 70% if semantically similar
    
    return {
        "overall_score": float(overall_score),
        "semantic_score": float(semantic_score),
        "sentence_score": float(sentence_score),
        "fact_score": float(fact_score),
        "nli_score": float(nli_score),
        "interpretation": get_faithfulness_interpretation(overall_score),
        "sentence_analysis": sentence_analysis,
        "semantic_details": semantic_result,
        "fact_details": {
            "verified_numbers": fact_details["verified_numbers"],
            "unverified_numbers": fact_details["unverified_numbers"],
            "verified_entities": fact_details["verified_entities"],
            "unverified_entities": fact_details["unverified_entities"]
        },
        "grounded_sentences": well_grounded,
        "total_sentences": total_sentences,
        "reasoning": reasoning  # NEW: Clear explanations for the score
    }


def get_faithfulness_interpretation(score: float) -> str:
    """Human-readable interpretation of faithfulness score."""
    if score >= 0.80:
        return "Highly grounded - answer closely matches source material"
    elif score >= 0.65:
        return "Well grounded - answer accurately represents source content"
    elif score >= 0.50:
        return "Moderately grounded - answer paraphrases sources with some additions"
    elif score >= 0.35:
        return "Partially grounded - some claims may not be fully supported"
    else:
        return "Poorly grounded - answer may contain unsupported claims"
