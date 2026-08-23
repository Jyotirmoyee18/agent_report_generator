FROM python:3.11-slim
WORKDIR /app

# Copy the whole project (backend needs orchestrator.py, agents/, tools/,
# state.py, config.py from the root) — build context must be the project
# root, not backend/. See docker-compose.yml.
COPY . .

RUN pip install --no-cache-dir -r backend/requirements.txt

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
