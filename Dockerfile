FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL/psycopg2 and health checks
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements files and install python dependencies
COPY backend/requirements.txt ./backend_requirements.txt
COPY frontend/requirements.txt ./frontend_requirements.txt

RUN pip install --no-cache-dir -r ./backend_requirements.txt
RUN pip install --no-cache-dir -r ./frontend_requirements.txt

# Copy source folders and files
COPY backend ./backend
COPY frontend ./frontend
COPY start.sh .

RUN chmod +x start.sh

# Expose the default Hugging Face Spaces port
EXPOSE 7860

CMD ["./start.sh"]
