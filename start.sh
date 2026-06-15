#!/bin/bash

# Start FastAPI backend in the background on port 8000
cd /app/backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 &

# Wait for backend to start up
echo "Waiting for backend to start..."
for i in {1..30}; do
  if curl -s http://127.0.0.1:8000/health > /dev/null; then
    echo "Backend is up and running!"
    break
  fi
  sleep 1
done

# Start Streamlit frontend on port 7860 (Hugging Face default port)
cd /app/frontend
export API_URL="http://127.0.0.1:8000"
streamlit run app.py --server.port=7860 --server.address=0.0.0.0
