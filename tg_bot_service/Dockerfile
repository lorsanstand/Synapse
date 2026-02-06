FROM python:3.14.2-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY tg_bot_service/pyproject.toml tg_bot_service/poetry.lock ./
COPY lib/ /lib

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY tg_bot_service/app/ ./app
COPY tg_bot_service/alembic.ini .
COPY tg_bot_service/scripts/ ./scripts/

RUN chmod +x /app/scripts/prestart.sh

CMD ["python", "-m", "app.main"]