FROM python:3.12-slim AS build
WORKDIR /src

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

COPY . .

FROM python:3.12-slim
WORKDIR /app

COPY --from=build /usr/local /usr/local
COPY --from=build /src /app

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV BACKEND_PORT=80

EXPOSE 80

ENTRYPOINT ["python", "/app/__main__.py"]
