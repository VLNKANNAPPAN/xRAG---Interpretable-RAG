# Ollama Setup Guide - 100% FREE Local LLM

## What is Ollama?

Ollama lets you run large language models **locally on your computer** - completely FREE with:
- ✅ **No API limits**
- ✅ **No rate limits**
- ✅ **No monthly quotas**
- ✅ **Complete privacy** (runs offline)
- ✅ **Fast responses**

## Quick Setup (5 minutes)

### Step 1: Install Ollama

**Windows:**
1. Download from: https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically

**Mac:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Step 2: Download a Model

Open terminal/PowerShell and run:

```bash
# Recommended: Fast 3B model (3GB download)
ollama pull llama3.2:3b

# Alternative: Very fast 1B model (1GB download)
ollama pull llama3.2:1b

# Alternative: Better quality 7B model (4GB download)
ollama pull mistral:7b
```

### Step 3: Verify Installation

```bash
# Check if Ollama is running
ollama list

# Test the model
ollama run llama3.2:3b "Hello, how are you?"
```

### Step 4: Restart Backend

The backend will automatically connect to Ollama at `http://localhost:11434`

```bash
# Backend will auto-reload
# No configuration needed!
```

## Available Models

| Model | Size | Speed | Quality | RAM Needed |
|-------|------|-------|---------|------------|
| `llama3.2:1b` | 1GB | ⚡⚡⚡ | ⭐⭐ | 4GB |
| `llama3.2:3b` | 3GB | ⚡⚡ | ⭐⭐⭐ | 8GB |
| `phi3:mini` | 2GB | ⚡⚡ | ⭐⭐⭐ | 6GB |
| `qwen2.5:3b` | 3GB | ⚡⚡ | ⭐⭐⭐⭐ | 8GB |
| `mistral:7b` | 4GB | ⚡ | ⭐⭐⭐⭐ | 12GB |

**Recommended**: `llama3.2:3b` - Best balance of speed and quality

## Configuration

### Change Model

Edit `.env` file:
```bash
OLLAMA_MODEL=llama3.2:3b
```

Or use environment variable:
```powershell
$env:OLLAMA_MODEL="qwen2.5:3b"
```

### Change Ollama URL

If running Ollama on different port/server:
```bash
OLLAMA_BASE_URL=http://localhost:11434
```

## Troubleshooting

### Error: "Ollama is not running"

**Solution:**
```bash
# Start Ollama service
ollama serve
```

### Slow responses?

**Solutions:**
1. Use smaller model: `ollama pull llama3.2:1b`
2. Close other applications
3. Ensure you have enough RAM

### Model not found?

**Solution:**
```bash
# Pull the model first
ollama pull llama3.2:3b

# Verify it's downloaded
ollama list
```

## Benefits vs HuggingFace

| Feature | HuggingFace | Ollama |
|---------|-------------|--------|
| Cost | Free tier (limited) | 100% Free |
| Rate Limits | 30k/month | ∞ Unlimited |
| Speed | Network dependent | Local (fast) |
| Privacy | Cloud-based | Fully private |
| Setup | API key needed | One-time install |

## System Requirements

**Minimum:**
- 8GB RAM
- 10GB disk space
- Any modern CPU

**Recommended:**
- 16GB RAM
- 20GB disk space
- GPU (optional, for faster inference)

## Next Steps

1. Install Ollama
2. Pull a model (`ollama pull llama3.2:3b`)
3. Restart backend - it will auto-connect!
4. Enjoy unlimited free queries! 🚀

## Advanced: GPU Acceleration

If you have NVIDIA GPU:
```bash
# Ollama automatically uses GPU if available
# No configuration needed!
```

Check GPU usage:
```bash
nvidia-smi
```
