# GoalPilot

Monorepo skeleton project.

## Cấu trúc thư mục:
- `apps/backend/`: chứa các service backend của dự án.
  - `input/`: khung cho phần tiếp nhận dữ liệu đầu vào như manual entry, SMS reading, OCR ingestion.
  - `intelligence/`: khung cho forecasting, reasoning, recommendation, và AI-related logic.
  - `data/`: khung cho data access, persistence, database interaction, và external data provider integration nếu sau này cần.
- `apps/frontend/`: khung cho mobile/web frontend.
- `docs/`: để tài liệu dự án.
- `infra/`: để deployment/configuration/docker về sau.
- `packages/`: để shared package hoặc shared types nếu sau này cần.
