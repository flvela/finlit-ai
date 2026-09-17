# Finlit AI Assistant
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/built%20with-Streamlit-FF4B4B.svg)
![LangChain](https://img.shields.io/badge/agent-LangChain-1C3C3C.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agents-2C3E50)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Database-orange)

> A financial education multi-agent AI assistant that specialized in Financial Literarcy and Investment insights.

## Table of Contents
1. [Quick Start](#-quick-start)
2. [Project Structure](#project-structure)

## 🚀 Quick Start

### 1. Create a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
py -m venv .venv
```

**macOS/Linux:**
```bash
python3 -m venv .venv
```

### 2. Activate the virtual environment

**Windows (PowerShell):**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bat
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install --upgrade pip
pip install -e .
```


### 4. Configure Model and Embeddings Provider

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

Then edit `.env` and set model and embeddings config. For an example:
```env
MODEL_PROVIDER=anthropic
MODEL_API_KEY=your_anthropic_api_key
MODEL=anthropic/claude-haiku-4-5-20251001
EMBEDDINGS_MODEL_PROVIDER=huggingface
EMBEDDINGS_MODEL_API_KEY=your_hugging_face_api_key
EMBEDDINGS_MODEL=google/embeddinggemma-300m
```
>&#128161; Model providers are based on [LangChain providers](https://reference.langchain.com/python/langchain/chat_models/base/init_chat_model#parameters). Currently only anthropic and openai are tested. 

>&#128161; Embeddings providers are based on [LangChain providers](https://reference.langchain.com/python/langchain/embeddings/base/init_embeddings#parameters). Currently only hugging face and openai implemented.

To test your config see [unit tests](#6-Run-Tests)


### 5. Build and Install locally
#### 5.1 Regular install
```bash
python3 -m build
pip install .
```

#### 5.2 Editable install
Changes to source code reflect instantly with no re-install
```bash
python3 -m build
pip install -e .
```

### 6. Run Tests
#### 6.1 Test your configuration
This is a recommended test to ensure your .env is properly configured
```bash
pytest tests/tools/test_config.py
```

#### 6.2 Run All tests
```bash
pytest
```

## Project Structure
```
FINLIT-AI/                        #entire application
  .github/workflows               #github repo actions or workflows
    python-app.yml                #python pull request action for building, testing and code coverage
  data/                           #contains financial literacy data used by AI assisstant
    aicpa_article.json            #AICPA financial literacy articles
    investopedia_articles.json    #Investopedia financial literacy articles
  src/                            #python source code
    agents/                       #python code related to LangGraph node, context schema and state
      __init__.py                 #package init file
    frontend/                     #streamlit application
    tools/                        #tools used for the agents to import sample data and config
      __init__.py                 #package init file
      articles.py                 #loads financial literacy articles used by AI assistant for agentic RAG
      config.py                   #gets the embeddings and chat model from the config .env file
      vector_store.py             #Chroma DB store functionality for local persistence
    __init__.py                   #package init file
  tests/                          #python unit tests using pytest
    agents/                       #agent unit tests 
    tools/                        #tools unit tests
      test_config.py              #config unit tests
      test_vector_store.py        #vector store unit tests
  .env.example                    #example config file
  .gitignore                      #git ignore file
  LICENSE                         #license information
  pyproject.toml                  #python project file
  README.md                       #this file 
```