FROM python:3.12-slim

WORKDIR /app

# Install Docker CLI and Docker Compose
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -fsSL https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose && \
    curl -fsSLO https://download.docker.com/linux/static/stable/x86_64/docker-24.0.7.tgz && \
    tar xzvf docker-24.0.7.tgz --strip 1 -C /usr/local/bin docker/docker && \
    rm docker-24.0.7.tgz && \
    apt-get purge -y curl && apt-get autoremove -y

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY setup_wizard.py .
COPY templates/ templates/

# Create config directory
RUN mkdir -p /app/config

EXPOSE 8080

CMD ["python", "app.py"]