# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies first (cache better)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything
COPY . .

# Expose Cloud Run port (always 8080)
EXPOSE 8080

# Start FastAPI using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]