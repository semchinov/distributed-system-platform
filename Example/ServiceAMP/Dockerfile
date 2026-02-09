FROM python:3.12-slim AS build
WORKDIR /src

COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry \
    && poetry export --format requirements.txt --without-hashes --output requirements.txt \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt

COPY . .

FROM python:3.12-slim
WORKDIR /app

COPY --from=build /install /usr/local
COPY --from=build /src /app

ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV BACKEND_PORT=80

EXPOSE 80

ENTRYPOINT ["python", "/app/__main__.py"]
