# ---------------------------------------------------------
# Stage 1: build do frontend (Vite React)
# ---------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copia manifestos e instala dependências
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copia código do frontend e gera build
COPY frontend ./
RUN npm run build

# ---------------------------------------------------------
# Stage 2: backend + runtime Python
# ---------------------------------------------------------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências de sistema (para numpy/pandas, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia código do backend
COPY backend ./backend

# Copia build do frontend gerado no stage 1
COPY --from=frontend-builder /app/frontend/dist ./frontend_dist

# Cria diretório de dados para o SQLite
RUN mkdir -p /app/data

# URL padrão do banco (pode ser sobrescrita via variável de ambiente)
ENV DATABASE_URL=sqlite:///data/app.db

EXPOSE 8000

# Ponto de trabalho do backend
WORKDIR /app/backend

# Comando de execução (modo "produção", sem reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
