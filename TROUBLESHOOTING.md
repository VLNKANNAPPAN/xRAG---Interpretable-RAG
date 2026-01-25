# Troubleshooting Guide: Command Not Found Errors

## Problem: "uvicorn" is not recognized

You encountered the following error when running `uvicorn backend.main:app --reload`:

```text
uvicorn : The term 'uvicorn' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

### Why this happens
This error occurs even when `uvicorn` is installed because the directory containing Python script executables (like `uvicorn.exe`, `pip.exe`, etc.) is not in your system's **PATH** environment variable. Windows doesn't know where to look for the command.

## Solutions

### Option 1: The Robust Way (Recommended)
Instead of relying on the command name directly, run it as a Python module. This always works as long as Python is installed and the package is in your environment.

**Command:**
```powershell
python -m uvicorn backend.main:app --reload
```
*Why this works:* It asks the `python` executable (which is in your path) to find the module `uvicorn` and run it.

### Option 2: The Permanent Fix (Adding to PATH)
To be able to type just `uvicorn` (or other tools like `black`, `pytest`, etc.), you need to add the Python Scripts directory to your PATH.

1.  **Find your Python Scripts path**:
    Run `pip show uvicorn` and look at the `Location`.
    *Example:* If location is `C:\Users\computer\AppData\Local\Programs\Python\Python313\Lib\site-packages`, the scripts are usually in:
    `C:\Users\computer\AppData\Local\Programs\Python\Python313\Scripts`

2.  **Add to Environment Variables**:
    *   Press `Win` key and search for "Edit the system environment variables".
    *   Click "Environment Variables".
    *   Under "User variables for [User]", find `Path` and click "Edit".
    *   Click "New" and paste the full path to the `Scripts` folder.
    *   Click OK on all windows.
    *   **Restart your terminal** for changes to take effect.

## Troubleshooting Similar Errors
If you see "`xyz` is not recognized..." for other Python tools:

1.  **Check Installation**: Run `pip show xyz` to ensure it's installed.
2.  **Try Module Execution**: Try running `python -m xyz`. This works for most tools (e.g., `python -m pip`, `python -m virtualenv`).
3.  **Check Environment**: Ensure you are in the correct virtual environment if you are using one.
