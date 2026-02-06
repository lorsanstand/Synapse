FROM python:3.14.2-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY schedule_service/pyproject.toml schedule_service/poetry.lock ./
COPY lib/ /lib/

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY schedule_service/app/ ./app

CMD ["python", "-m", "app.main"]