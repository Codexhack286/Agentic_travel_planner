# Use official Python slim image for runtime efficiency
FROM python:3.11-slim

# Install build dependencies required for compiling certain Python modules
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Astral UV for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependencies manifest and lock file
COPY pyproject.toml uv.lock ./

# Install project dependencies without installing the project itself
RUN uv sync --frozen --no-cache --no-install-project

# Copy both the backend and agent folders to preserve directory hierarchy
COPY backend/ /app/backend/
COPY ai-travel-concierge/ /app/ai-travel-concierge/

# Expose API port
EXPOSE 8000

# Configure environment variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONPATH=/app/backend:/app/ai-travel-concierge
ENV PYTHONUNBUFFERED=1

# Change context to the backend folder
WORKDIR /app/backend

# Launch FastAPI app with Uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
