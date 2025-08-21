## FastCrew: FastAPI + CrewAI (Azure OpenAI)

### Prerequisites
- Python 3.11 (3.12 also works)
- Azure OpenAI deployment
- Optional: Supabase project (for persistence) and Google Auth in frontend

### Setup
1. Create and activate a virtual environment (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Install dependencies:
```powershell
pip install -r requirements.txt
```
3. Configure environment variables in `.env`:
```
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
# Optional Supabase
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
```
4. Run the server:
```powershell
uvicorn app.main:app --reload --port 8000
```

### Auth
- Pass `Authorization: Bearer <jwt>` header. For local dev, you may pass `X-User-Id: <user-id>` and omit Authorization.

### Endpoints
- `POST /chat` -> { message } => { reply }
- `POST /marketing/research` -> { company, product, target_markets[] } => { user_id, insights }
- `POST /marketing/plan` -> { company, product, research_insights } => { user_id, plan, score }
- `POST /marketing/content` -> { company, product, plan, platforms? } => { user_id, content }

If Supabase is configured, results are stored per-user in tables `marketing_research`, `marketing_plan`, and `marketing_content`.

