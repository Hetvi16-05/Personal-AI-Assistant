FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL/psycopg2 and health checks
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file and install backend python dependencies
COPY backend/requirements.txt ./backend_requirements.txt

RUN pip install --no-cache-dir -r ./backend_requirements.txt

# Copy source folders and files
COPY backend ./backend
COPY start.sh .

RUN chmod +x start.sh

# Expose backend port
EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
