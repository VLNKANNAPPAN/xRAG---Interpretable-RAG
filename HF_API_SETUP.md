# Hugging Face API Configuration

## Get Your Free API Key

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it "xRAG" and select "Read" access
4. Copy the token (starts with `hf_`)

## Set Your API Key

### Option 1: Environment Variable (Recommended)
```bash
# Windows PowerShell
$env:HF_API_KEY="hf_your_token_here"

# Windows CMD
set HF_API_KEY=hf_your_token_here

# Linux/Mac
export HF_API_KEY="hf_your_token_here"
```

### Option 2: Direct in Code
Edit `backend/generation/generator.py` line 7:
```python
HF_API_KEY = "hf_your_actual_token_here"
```

## Available Free Models

Current model: **Meta-Llama-3.1-8B-Instruct**

Alternative models you can use (change line 8 in generator.py):

1. **Mistral 7B** (Fast, good quality)
   ```python
   HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
   ```

2. **Qwen 2.5 7B** (Excellent for RAG)
   ```python
   HF_API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"
   ```

3. **Phi-3 Mini** (Lightweight, fast)
   ```python
   HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/Phi-3-mini-4k-instruct"
   ```

## Free Tier Limits

- **30,000 requests/month** (1,000/day)
- No credit card required
- Rate limit: ~100 requests/minute
- Much better than Gemini's 20/day!

## Troubleshooting

If you get "Model is loading" error:
- Wait 20-30 seconds for the model to load (first request only)
- Subsequent requests will be fast

If you get 401 Unauthorized:
- Check your API key is correct
- Make sure it starts with `hf_`
- Verify the token has "Read" access
