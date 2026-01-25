"""
Faithfulness scoring using NLI (Natural Language Inference) models.
Checks if generated answers are entailed by retrieved chunks.
"""

from typing import List, Dict, Tuple
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import nltk
from functools import lru_cache

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class FaithfulnessScorer:
    """
    Uses a DeBERTa-based NLI model to score faithfulness of answers.
    """
    
    def __init__(self, model_name: str = "microsoft/deberta-v3-base"):
        """
        Initialize the NLI model for faithfulness scoring.
        
        Args:
            model_name: HuggingFace model identifier for NLI
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Use a smaller, faster model for NLI
        # Alternative: "cross-encoder/nli-deberta-v3-small" for faster inference
        nli_model = "cross-encoder/nli-deberta-v3-small"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(nli_model)
            self.model = AutoModelForSequenceClassification.from_pretrained(nli_model)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Warning: Could not load NLI model {nli_model}: {e}")
            print("Faithfulness scoring will use fallback semantic similarity")
            self.model = None
            self.tokenizer = None
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using NLTK."""
        try:
            sentences = nltk.sent_tokenize(text)
            return [s.strip() for s in sentences if s.strip()]
        except:
            # Fallback: simple split on periods
            return [s.strip() + '.' for s in text.split('.') if s.strip()]
    
    def _check_entailment(self, premise: str, hypothesis: str) -> float:
        """
        Check if hypothesis is entailed by premise using NLI model.
        
        Returns:
            Entailment score (0-1), where 1 = fully entailed
        """
        if self.model is None or self.tokenizer is None:
            # Fallback: use simple semantic similarity
            from backend.explainability.similarity import semantic_similarity
            return semantic_similarity(premise, hypothesis)
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                premise,
                hypothesis,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            ).to(self.device)
            
            # Get model prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1)
            
            # For NLI models: [contradiction, neutral, entailment]
            # We want the entailment probability
            entailment_score = probs[0][2].item()
            
            return entailment_score
            
        except Exception as e:
            print(f"Error in entailment check: {e}")
            return 0.5  # Neutral score on error
    
    def score_faithfulness(
        self,
        answer: str,
        chunks: List[str],
        return_details: bool = False
    ) -> Dict:
        """
        Score the faithfulness of an answer against retrieved chunks.
        
        Args:
            answer: Generated answer text
            chunks: List of retrieved chunk texts
            return_details: If True, return per-sentence scores
        
        Returns:
            Dictionary with:
                - faithfulness_score: Overall score (0-1)
                - unsupported_claims: List of sentences with low entailment
                - sentence_scores: Per-sentence entailment scores (if return_details=True)
        """
        # Split answer into sentences
        answer_sentences = self._split_into_sentences(answer)
        
        if not answer_sentences:
            return {
                "faithfulness_score": 1.0,
                "unsupported_claims": [],
                "sentence_scores": []
            }
        
        # Combine all chunks into context
        context = "\n\n".join(chunks)
        
        # Score each sentence
        sentence_scores = []
        unsupported_claims = []
        
        for sentence in answer_sentences:
            # Check entailment against full context
            score = self._check_entailment(context, sentence)
            sentence_scores.append({
                "sentence": sentence,
                "score": score
            })
            
            # Flag as unsupported if score is low
            if score < 0.5:  # Threshold for unsupported claims
                unsupported_claims.append(sentence)
        
        # Calculate overall faithfulness score
        if sentence_scores:
            overall_score = np.mean([s["score"] for s in sentence_scores])
        else:
            overall_score = 1.0
        
        result = {
            "faithfulness_score": float(overall_score),
            "unsupported_claims": unsupported_claims,
            "num_sentences": len(answer_sentences),
            "num_unsupported": len(unsupported_claims)
        }
        
        if return_details:
            result["sentence_scores"] = sentence_scores
        
        return result


# Global instance (lazy loaded)
_scorer_instance = None


def get_scorer() -> FaithfulnessScorer:
    """Get or create global faithfulness scorer instance."""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = FaithfulnessScorer()
    return _scorer_instance


def calculate_faithfulness_score(
    answer: str,
    chunks: List[str],
    return_details: bool = False
) -> Dict:
    """
    Convenience function to calculate faithfulness score.
    
    Args:
        answer: Generated answer text
        chunks: List of retrieved chunk texts
        return_details: If True, return per-sentence scores
    
    Returns:
        Dictionary with faithfulness metrics
    """
    scorer = get_scorer()
    return scorer.score_faithfulness(answer, chunks, return_details)
