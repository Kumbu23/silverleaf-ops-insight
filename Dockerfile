FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend backend
COPY sample_data/ /app/sample_data/
COPY streamlit_app.py /app/streamlit_app.py

# Expose port
EXPOSE 8501

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run Streamlit app
CMD ["streamlit", "run", "/app/streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]
