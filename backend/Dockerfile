# Use an ARM-compatible base image if needed
FROM --platform=linux/arm64 python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (if needed for FAISS and others)
RUN apt-get update && apt-get install -y \
    build-essential wget curl && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install additional libraries (if not in requirements.txt)
RUN pip install sentence-transformers faiss-cpu

# Copy the backend code into the container
COPY backend /app/backend
COPY scripts /app/scripts
COPY data /app/data

# Set the PYTHONPATH environment variable to make the `backend` directory importable
ENV PYTHONPATH=/app:/app/backend

# Expose the backend port
EXPOSE 8000

# Command to run the backend service
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]