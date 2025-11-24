# ==== BLOCK: BASE_IMAGE - START ====
FROM python:3.11-slim
# ==== BLOCK: BASE_IMAGE - END ====


# ==== BLOCK: SYSTEM_DEPENDENCIES - START ====
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*
# ==== BLOCK: SYSTEM_DEPENDENCIES - END ====


# ==== BLOCK: WORKDIR_SETUP - START ====
WORKDIR /app
# ==== BLOCK: WORKDIR_SETUP - END ====


# ==== BLOCK: PYTHON_DEPENDENCIES_INSTALL - START ====
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt
# ==== BLOCK: PYTHON_DEPENDENCIES_INSTALL - END ====


# ==== BLOCK: BACKEND_CODE_COPY - START ====
COPY backend /app/backend
# ==== BLOCK: BACKEND_CODE_COPY - END ====


# ==== BLOCK: FRONTEND_INSTALL_BUILD - START ====
COPY frontend/package.json /app/frontend/package.json
COPY frontend/vite.config.js /app/frontend/vite.config.js
COPY frontend/index.html /app/frontend/index.html
COPY frontend/src /app/frontend/src

WORKDIR /app/frontend
RUN npm install && npm run build
# ==== BLOCK: FRONTEND_INSTALL_BUILD - END ====


# ==== BLOCK: WORKDIR_BACK_TO_APP - START ====
WORKDIR /app
ENV FRONTEND_DIST_DIR=/app/frontend/dist
# ==== BLOCK: WORKDIR_BACK_TO_APP - END ====


# ==== BLOCK: SQLITE_DATA_DIR - START ====
RUN mkdir -p /app/data
# ==== BLOCK: SQLITE_DATA_DIR - END ====


# ==== BLOCK: EXPOSE_AND_CMD - START ====
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
# ==== BLOCK: EXPOSE_AND_CMD - END ====
