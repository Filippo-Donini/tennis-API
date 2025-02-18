FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for psycopg2 and cron
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    python3-dev \
    libpq-dev \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure the templates directory exists
RUN mkdir -p templates static

# Make the setup script executable
COPY setup-cron.sh /app/setup-cron.sh
RUN chmod +x /app/setup-cron.sh

EXPOSE 8000

# Use a shell script to start both cron and uvicorn
CMD ["/bin/bash", "-c", "/app/setup-cron.sh && uvicorn main:app --host 0.0.0.0 --port 8000"]
