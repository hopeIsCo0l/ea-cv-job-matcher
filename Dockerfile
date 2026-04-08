FROM python:3.11-slim

WORKDIR /app

ENV PIP_DEFAULT_TIMEOUT=120

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY scripts /app/scripts
COPY registry /app/registry
COPY config /app/config

RUN python -m pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
