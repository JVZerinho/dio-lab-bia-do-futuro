# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr and enforces UTF-8.
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install dependencies before copying source code to leverage Docker layer caching.
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container with appropriate permissions.
COPY --chown=appuser:appuser . .

# Switch to the non-privileged user to run the application.
USER appuser

# Run the interactive CLI application.
CMD ["python", "src/app.py"]
