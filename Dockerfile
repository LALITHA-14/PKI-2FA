# Stage 1: builder
FROM python:3.11-slim AS builder
WORKDIR /app

# Install build deps for any packages that need them (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m pip install --upgrade pip
# install into target prefix to copy to runtime
RUN pip install --prefix=/install -r requirements.txt

# Stage 2: runtime
FROM python:3.11-slim
ENV TZ=UTC
WORKDIR /app

# Install runtime system deps (cron + utilities)
RUN apt-get update && apt-get install -y --no-install-recommends cron ca-certificates curl && rm -rf /var/lib/apt/lists/*

# Copy python packages from builder
COPY --from=builder /install /usr/local

# Copy app code
COPY . /app

# Ensure cron file has LF endings inside image (strip CR if any)
RUN if [ -f /app/cron/2fa-cron ]; then sed -i 's/\r$//' /app/cron/2fa-cron; fi

# Install cron file
RUN chmod 0644 /app/cron/2fa-cron && crontab /app/cron/2fa-cron

# Create persistent mount points
RUN mkdir -p /data /cron
VOLUME ["/data", "/cron"]

EXPOSE 8080

# Start cron and uvicorn. Use shell form so both start.
CMD service cron start && uvicorn app.main:app --host 0.0.0.0 --port 8080
