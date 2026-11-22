# 24/7 Cloud Observatory Container (Hugging Face Spaces / Render / Railway / Fly.io)
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY README.md ./README.md

ENV COSMOS_SPEED=6
EXPOSE 7860

CMD ["python", "-m", "uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "7860"]
