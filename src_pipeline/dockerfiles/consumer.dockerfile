FROM python:3.13-slim

# Copy the pre-built uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Enable bytecode compilation and unbuffered terminal output
ENV UV_COMPILE_BYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install project dependencies first (for layer caching)
COPY pyproject.toml uv.lock* /app/
RUN uv sync --frozen --no-dev --no-install-project

# Copy application source files
COPY src_pipeline/consumer.py /app/
COPY src_pipeline/utils /app/utils

CMD ["uv", "run", "python", "-u", "consumer.py"]