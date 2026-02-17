# Windows Installation Guide - Fixing hnswlib Build Error

## ⚠️ Important: Python Version Issue

**You're using Python 3.14.2**, which is very new. Many packages (including `chroma-hnswlib`) don't have pre-built wheels for Python 3.14 yet, so pip tries to build from source, which requires C++ build tools.

**Recommended:** Use Python 3.11 or 3.12 for better package compatibility. However, if you want to stick with 3.14, you'll need the C++ Build Tools.

## Quick Solutions (Try in Order)

### Solution 1: Install Pre-built Wheels (Easiest - Try This First)

Try installing with pre-built wheels. Sometimes pip tries to build from source when wheels are available:

```bash
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt --only-binary :all:
```

If that doesn't work, try installing chromadb separately with a specific version:

```bash
pip install chromadb --prefer-binary
pip install -r requirements.txt
```

### Solution 2: Install Microsoft C++ Build Tools (REQUIRED for Python 3.14)

**Since you're using Python 3.14, this is likely your best option** because most packages don't have pre-built wheels yet.

This is the official solution and will allow you to build packages that require compilation:

1. **Download Microsoft C++ Build Tools:**
   - Visit: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Download "Build Tools for Visual Studio"

2. **Install:**
   - Run the installer
   - Select "Desktop development with C++" workload
   - Make sure "Windows 10 SDK" (or Windows 11 SDK) is checked
   - Click Install (this will take several minutes and ~6GB of space)

3. **Restart your terminal/PowerShell** after installation

4. **Try installing again:**
   ```bash
   pip install -r requirements.txt
   ```

### Solution 3: Use Alternative Installation Method

Try installing chromadb with specific flags:

```bash
pip install --upgrade pip setuptools wheel
pip install chromadb --no-build-isolation
pip install -r requirements.txt
```

### Solution 4: Install Dependencies One by One

Sometimes installing dependencies individually helps identify the issue:

```bash
pip install fastapi uvicorn
pip install langchain langchain-community langchain-openai langgraph
pip install pypdf python-dotenv openai
pip install chromadb
```

### Solution 5: Use Conda/Miniconda (Alternative Python Environment)

If you have conda installed or are willing to install it:

```bash
conda create -n student_loan python=3.11
conda activate student_loan
conda install -c conda-forge chromadb
pip install -r requirements.txt
```

Conda often has pre-built binaries that avoid compilation issues.

## Which Solution Should You Use?

**For Python 3.14 (your current version):**
- **Use Solution 2** - Install Microsoft C++ Build Tools (this is the most reliable option)
- **OR Use Solution 6** - Switch to Python 3.11 or 3.12 (recommended for better compatibility)

**For Python 3.11/3.12:**
- **Start with Solution 1** - It's the quickest and often works
- **If Solution 1 fails, use Solution 2** - Install C++ Build Tools
- **Solution 5** is good if you're already using conda

### Solution 6: Use Python 3.11 or 3.12 (Recommended)

Python 3.14 is very new and many packages don't have pre-built wheels yet. Using Python 3.11 or 3.12 will give you better compatibility:

1. **Download Python 3.12** from https://www.python.org/downloads/
2. **Install it** (you can have multiple Python versions)
3. **Create a virtual environment with Python 3.12:**
   ```bash
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Or if Python 3.12 is your default:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## After Successful Installation

Once everything is installed, verify the installation:

```bash
python -c "import chromadb; print('ChromaDB installed successfully!')"
python -c "import fastapi; print('FastAPI installed successfully!')"
```

Then you can start the backend:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

