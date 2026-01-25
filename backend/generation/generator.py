from typing import List
import os
from openai import OpenAI

# Groq API - FREE tier: 14,400 requests/day (30 req/min)
# Get your free API key from: https://console.groq.com
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Initialize Groq client
client = None
if GROQ_API_KEY:
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )

# Available Groq models (as of Jan 2025):
# - "llama-3.3-70b-versatile" - Best quality, 128k context
# - "llama-3.1-8b-instant" - Fastest, good quality
# - "mixtral-8x7b-32768" - Long context window
# - "gemma2-9b-it" - Google's Gemma model

GROQ_MODEL = "llama-3.3-70b-versatile"  # Default model

SYSTEM_PROMPT = """You are an AI assistant that answers questions using ONLY the provided context.

CRITICAL RULES:
1. **MUST use exact phrases or facts from the context** - Copy relevant sentences directly
2. **DO NOT use general knowledge** - Only answer from the given context
3. **If information exists in context, YOU MUST provide it** - Don't say "not enough information" if the answer is there
4. **Formatting**:
   - Use **tables** for comparisons
   - Use **bullet points** for lists or steps
   - Keep paragraphs short and concise
   - Use markdown formatting (bolding key terms)
5. **If the answer truly cannot be found in context**, only then say: "Not enough information to answer."

IMPORTANT: Read the context carefully and extract ALL relevant information before answering.
"""


def build_context(chunks: List[str]) -> str:
    """
    Combine retrieved chunks into a single context block with clear separation.
    """
    if not chunks:
        return "No context available."
    
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(f"--- Source {i+1} ---\n{chunk}\n")
    
    return "\n".join(context_parts)


def generate_answer(query: str, chunks: List[str], model: str = GROQ_MODEL) -> str:
    """
    Generate an answer using Groq API.
    
    Args:
        query: User's question
        chunks: Retrieved context chunks
        model: Groq model to use
    
    Returns:
        Generated answer as string
    """
    if not GROQ_API_KEY:
        return "Error: GROQ_API_KEY not set. Please add it to your .env file. Get a free key at: https://console.groq.com"
    
    if not client:
        return "Error: Groq client not initialized. Please check your API key."
    
    context = build_context(chunks)
    
    # Construct messages with system instruction
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""I have provided you with context from multiple sources below. Please read ALL sources carefully.

{context}

Question: {query}

Instructions:
1. Read through ALL the sources above
2. Extract ONLY relevant information that answers the question
3. Combine information from multiple sources if needed
4. Provide a clear, well-formatted answer using markdown
5. If the answer exists in the context, YOU MUST provide it

Answer:"""
        }
    ]
    
    try:
        # Generate response
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=800,
            top_p=0.9,
        )
        
        answer = response.choices[0].message.content
        return answer.strip() if answer else "Unable to generate answer."
        
    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() and "key" in error_msg.lower():
            return "Error: Invalid Groq API key. Please check your .env file. Get a free key at: https://console.groq.com"
        elif "rate_limit" in error_msg.lower() or "quota" in error_msg.lower():
            return "Error: Groq API rate limit reached. Free tier allows 14,400 requests/day (30 req/min). Please try again later."
        elif "404" in error_msg or "not found" in error_msg:
            # Model not found - try fallback
            print(f"Model {model} not found, trying fallback...")
            if model != "llama-3.1-8b-instant":
                return generate_answer(query, chunks, model="llama-3.1-8b-instant")
            else:
                return f"Error: Model not available. {error_msg}"
        else:
            print(f"Error calling Groq API: {e}")
            return f"Error generating answer: {str(e)}"


def generate_answer_with_fallback(query: str, chunks: List[str]) -> str:
    """
    Generate answer with automatic fallback through multiple Groq models.
    """
    groq_models = [
        "llama-3.3-70b-versatile",  # Primary: Best quality
        "llama-3.1-8b-instant",     # Fallback 1: Fastest
        "mixtral-8x7b-32768",       # Fallback 2: Long context
        "gemma2-9b-it",             # Fallback 3: Alternative
    ]
    
    if not GROQ_API_KEY or not client:
        return "Error: GROQ_API_KEY not set. Get a free key at: https://console.groq.com"
    
    context = build_context(chunks)
    last_error = None
    
    for model in groq_models:
        try:
            print(f"Trying Groq model: {model}")
            
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"""Context:
{context}

Question: {query}

Answer based ONLY on the context above:"""
                }
            ]
            
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3,
                max_tokens=800,
                top_p=0.9,
            )
            
            answer = response.choices[0].message.content
            
            if answer and answer.strip():
                print(f"✓ Successfully used model: {model}")
                return answer.strip()
                
        except Exception as e:
            print(f"✗ Model {model} failed: {e}")
            last_error = str(e)
            continue
    
    return f"All Groq models failed. Last error: {last_error}"


# Helper function to list available models (for debugging)
def list_available_models():
    """List all available Groq models."""
    if not GROQ_API_KEY:
        print("GROQ_API_KEY not set")
        return
    
    if not client:
        print("Groq client not initialized")
        return
    
    try:
        # Groq available models (manually listed as API doesn't have list endpoint)
        models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "llama-3.2-1b-preview",
            "llama-3.2-3b-preview",
            "llama-3.2-11b-vision-preview",
            "llama-3.2-90b-vision-preview",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
            "gemma-7b-it",
        ]
        
        print("Available Groq models:")
        for model in models:
            print(f"  - {model}")
            
    except Exception as e:
        print(f"Error listing models: {e}")


# Test function
def test_groq():
    """Test Groq API with a simple query."""
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set")
        print("Get your free API key from: https://console.groq.com")
        return
    
    print("✓ GROQ_API_KEY is set")
    print("\nTesting Groq API...\n")
    
    # Test chunks
    test_chunks = [
        "Paris is the capital of France. It has a population of approximately 2.2 million people.",
        "France is located in Western Europe. The official language is French."
    ]
    
    test_query = "What is the capital of France?"
    
    print(f"Query: {test_query}\n")
    
    # Test with fallback
    answer = generate_answer_with_fallback(test_query, test_chunks)
    
    print(f"\nAnswer:\n{answer}")