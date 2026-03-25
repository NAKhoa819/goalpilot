# GoalPilot

Monorepo gồm:
- `apps/backend`: FastAPI backend
- `apps/frontend`: React Native / Expo frontend
- `docs`: tài liệu dự án
- `infra`: hạ tầng và deployment
- `packages`: shared packages nếu cần

## Yêu cầu

Chạy local:
- Python 3.11+
- Node.js 18+
- SQL Server Express
- ODBC Driver 17 for SQL Server

Chạy bằng Docker:
- Docker Desktop

## Khởi tạo từ đầu

Tại thư mục gốc repo:

```powershell
git clone <repo-url>
cd goalpilot
```

Tạo file env từ mẫu:

```powershell
Copy-Item .env.example .env
```

Nếu dùng Git Bash hoặc WSL:

```bash
cp .env.example .env
```

Sau đó chỉnh lại các biến trong `.env`, tối thiểu:
- `EXPO_PUBLIC_API_URL`
- `ACTIVE_LLM_PROVIDER`, `BACKUP_PROVIDER`, `BACKUP_MODEL_ID`
- `GOOGLE_API_KEY` hoặc `GROQ_API_KEY` nếu dùng provider thật
- `DB_SERVER`

## Chạy local

### 1. Cài backend

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r apps/backend/requirements.txt
```

### 2. Cấu hình database local

Mặc định backend local dùng:

```env
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=swinhackathon_db
DB_DRIVER={ODBC Driver 17 for SQL Server}
DB_TRUSTED_CONNECTION=yes
DB_TRUST_SERVER_CERTIFICATE=yes
DB_ENCRYPT=no
```

Khi backend khởi động, app sẽ tự:
- tạo database `swinhackathon_db` nếu chưa có
- tạo schema cần thiết
- seed dữ liệu goal mặc định

### 3. Chạy backend

```powershell
cd apps/backend
..\..\venv\Scripts\python -m uvicorn main_api:app --host 0.0.0.0 --port 8000 --reload
```

Backend:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

### 4. Cài frontend

Mở terminal khác tại root repo:

```powershell
cd apps/frontend
npm install
```

### 5. Chạy frontend

Trong `.env`, đặt:

```env
EXPO_PUBLIC_API_URL=http://<IP_MAY_CUA_BAN>:8000
```

Ví dụ nếu test bằng điện thoại qua Expo Go, dùng IP LAN của máy thay vì `localhost`.

Chạy app:

```powershell
cd apps/frontend
npm start
```

## Chạy bằng Docker

Docker Compose sẽ chạy:
- SQL Server Express container
- backend container

Tại thư mục gốc repo:

```powershell
docker compose up --build
```

Khi chạy bằng Docker:
- backend lên tại `http://localhost:8000`
- SQL Server lên tại port `1433`
- backend tự tạo database `swinhackathon_db` và schema khi startup

Nếu muốn chạy nền:

```powershell
docker compose up --build -d
```

Dừng container:

```powershell
docker compose down
```

Xem log:

```powershell
docker compose logs -f backend
docker compose logs -f sqlserver
```

## Biến môi trường chính

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
- `CAR_PRICE_MODEL_OUTPUT_MULTIPLIER_VND`
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

## Lưu ý

- `.env` bị ignore bởi Git, không push file này lên repo.
- Dùng [`.env.example`](/d:/swin/swin2026/goalpilot/.env.example) làm mẫu chia sẻ cấu hình.
- Nếu Dashboard không lên, kiểm tra backend trước ở `/docs` và `/api/dashboard`.
