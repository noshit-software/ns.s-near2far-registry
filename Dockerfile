FROM python:3.12-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv sync --no-dev
COPY app/ ./app/

RUN groupadd -g 1000 appuser && useradd -u 1000 -g appuser -m appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app /home/appuser
USER appuser

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5102"]
