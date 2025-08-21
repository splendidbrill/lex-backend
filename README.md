## FastCrew: FastAPI + CrewAI (Azure OpenAI)

### Prerequisites
- Python 3.11
- Azure OpenAI resource and a chat model deployment

### Setup (Windows PowerShell)
1. Create and activate a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:
```powershell
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with:
```
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

4. Run the API server:
```powershell
uvicorn app.main:app --reload --port 8000
```

### Test the chat endpoint
```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/chat -ContentType 'application/json' -Body '{"message":"Hello!"}'
```

You should receive a JSON response with a `reply` field.

### Project structure
- `app/main.py`: FastAPI app
- `app/config.py`: Settings and Azure OpenAI config
- `app/agents.py`: CrewAI agent wrapper
- `app/routers/chat.py`: Chat API route

