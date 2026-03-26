# GoalPilot

Monorepo structure:
- `apps/backend`: FastAPI backend
- `apps/frontend`: React Native / Expo frontend
- `docs`: project documentation
- `infra`: infrastructure and deployment
- `packages`: shared packages if needed

## Requirements

For local development:
- Python 3.11+
- Node.js 18+
- SQL Server Express
- ODBC Driver 17 for SQL Server

For Docker:
- Docker Desktop

## Initial Setup

From the repository root:

```powershell
git clone <repo-url>
cd goalpilot
```

Create `.env` from the example:

```powershell
Copy-Item .env.example .env
```

If you use Git Bash or WSL:

```bash
cp .env.example .env
```

Then update the required values in `.env`, at minimum:
- `EXPO_PUBLIC_API_URL`
- `ACTIVE_LLM_PROVIDER`, `BACKUP_PROVIDER`, `BACKUP_MODEL_ID`
- `GOOGLE_API_KEY` or `GROQ_API_KEY` if you use a real provider
- `DB_SERVER`

## Run Locally

### 1. Install Backend Dependencies

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r apps/backend/requirements.txt
```

### 2. Configure Local Database

By default, the local backend uses:

```env
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=swinhackathon_db
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_TRUSTED_CONNECTION=yes
DB_TRUST_SERVER_CERTIFICATE=yes
DB_ENCRYPT=no
```

When the backend starts, it will automatically:
- create the `swinhackathon_db` database if it does not exist
- create the required schema
- seed default goal data

### 3. Run Backend

```powershell
cd apps/backend
..\..\venv\Scripts\python -m uvicorn main_api:app --host 0.0.0.0 --port 8000 --reload
```

Backend URLs:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### 4. Install Frontend Dependencies

Open another terminal at the repo root:

```powershell
cd apps/frontend
npm install
```

### 5. Run Frontend

In `.env`, set:

```env
EXPO_PUBLIC_API_URL=http://<YOUR_MACHINE_IP>:8000
```

If you test on a phone using Expo Go, use your machine's LAN IP instead of `localhost`.

Run the app:

```powershell
cd apps/frontend
npm start
```

## Run With Docker

Docker Compose runs:
- SQL Server container
- backend container

From the repo root:

```powershell
docker compose up --build
```

When running with Docker:
- backend is available at `http://localhost:8000`
- SQL Server is available on port `1433`
- backend automatically creates the `swinhackathon_db` database and schema on startup

To run in detached mode:

```powershell
docker compose up --build -d
```

To stop containers:

```powershell
docker compose down
```

To view logs:

```powershell
docker compose logs -f backend
docker compose logs -f sqlserver
```

## Main Environment Variables

Frontend:
- `EXPO_PUBLIC_API_URL`

Backend LLM:
- `ACTIVE_LLM_PROVIDER`
- `BACKUP_PROVIDER`
- `BACKUP_MODEL_ID`
- `GOOGLE_API_KEY`
- `GROQ_API_KEY`
- `BEDROCK_MODEL`

Backend SageMaker:
- `SAGEMAKER_REGION`
- `SAGEMAKER_CAR_PRICE_ENDPOINT_NAME`
- `SAGEMAKER_CAR_PRICE_CONTENT_TYPE`
- `SAGEMAKER_CAR_PRICE_ACCEPT`
- `SAGEMAKER_CAR_PRICE_REQUEST_FORMAT`
- `CAR_PRICE_MODEL_REFERENCE_YEAR`
- `CAR_PRICE_MODEL_OUTPUT_MULTIPLIER`
- `AWS_PROFILE`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`
- `AWS_DEFAULT_REGION`

Backend SQL Server local:
- `DB_SERVER`
- `DB_NAME`
- `DB_DRIVER`
- `DB_TRUSTED_CONNECTION`
- `DB_USER`
- `DB_PASSWORD`
- `DB_TRUST_SERVER_CERTIFICATE`
- `DB_ENCRYPT`

Docker SQL Server:
- `SQLSERVER_SA_PASSWORD`

## Notes

- `.env` is ignored by Git. Do not commit it.
- Use [`.env.example`](/d:/swin/swin2026/goalpilot/.env.example) as the shared configuration template.
- If the dashboard does not load, check the backend first at `/docs` and `/api/dashboard`.
