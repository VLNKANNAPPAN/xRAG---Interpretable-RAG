# Environment Variables Setup Guide

## Quick Setup

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API key:**
   ```
   HF_API_KEY=hf_your_actual_token_here
   ```

3. **Restart the backend server**

## Security Notes

✅ **Safe to commit:**
- `.env.example` - Template file with placeholder values
- `.gitignore` - Excludes sensitive files

❌ **NEVER commit:**
- `.env` - Contains your actual API keys
- Any file with real credentials

## Verifying Setup

The `.env` file is already added to `.gitignore`, so it won't be tracked by Git.

To verify:
```bash
git status
```

You should NOT see `.env` in the list of untracked files.

## Getting Your HuggingFace API Key

1. Go to https://huggingface.co/settings/tokens
2. Click "New token"
3. Name it "xRAG"
4. Select "Read" access
5. Copy the token (starts with `hf_`)
6. Paste it in your `.env` file

## Troubleshooting

If you get "HF_API_KEY not found" error:
1. Make sure `.env` file exists in the project root
2. Check that `HF_API_KEY=` has no spaces around the `=`
3. Restart the backend server after editing `.env`
