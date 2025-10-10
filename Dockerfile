# ===============================
# Base Image
# ===============================
FROM python:3.11-slim

# ===============================
# Set working directory
# ===============================
WORKDIR /app

# ===============================
# Install dependencies
# ===============================
# 먼저 requirements.txt 복사 후 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ===============================
# Copy application code
# ===============================
COPY ./app /app
COPY watchlist.txt /watchlist.txt

# ===============================
# Set environment variables (optional)
# ===============================
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# ===============================
# Run command
# ===============================
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
