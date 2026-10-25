FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend/ backend/
COPY --from=frontend /frontend/dist frontend/dist
RUN useradd -m torque && mkdir -p /app/data && chown -R torque:torque /app
USER torque
VOLUME ["/app/data"]
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "backend.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
