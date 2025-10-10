# ===============================
# Base Image
# ===============================
FROM python:3.10-slim

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
COPY ./app ./app

# ===============================
# Set environment variables (optional)
# ===============================
ENV PYTHONUNBUFFERED=1

# ===============================
# Run command
# ===============================
CMD ["python", "app/main.py"]
