FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home --uid 10001 worker \
    && mkdir -p /app/data/articles /state \
    && chown -R worker:worker /app /state

COPY --chown=worker:worker app ./app
COPY --chown=worker:worker main.py ./main.py

USER worker

ENTRYPOINT ["python", "main.py"]
CMD ["--sync", "--state-file", "/state/sync-state.json"]
