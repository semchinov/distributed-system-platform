# Service B (Python, FastAPI)
#### (by Mikhail on Python FastAPI)

Python-реализация сервиса B, функционально эквивалентная `Example/ServiceB` на C#.
Сервис принимает входящие сообщения и отдаёт метрики/трейсы через OpenTelemetry.

## Требования
- Python 3.12+
- Poetry
- Docker (опционально, для контейнерного запуска)

## Конфигурация
Настройки читаются из переменных окружения (см. `.env.example`):

| Переменная | Значение по умолчанию | Описание |
| --- | --- | --- |
| `SERVICE_NAME` | `service-b` | Имя сервиса для телеметрии |
| `OPENTELEMETRY_ENDPOINT` | `http://otel-collector:4317` | OTEL collector gRPC endpoint |
| `HOST` | `0.0.0.0` | Адрес биндинга |
| `BACKEND_PORT` | `80` | Порт приложения |

## Запуск локально
```bash
cp .env.example .env
poetry install
poetry run python __main__.py
```

## Запуск в Docker
```bash
docker build -t service-b-python .
docker run --rm -p 10002:80 --env-file .env service-b-python
```

## API
- `POST /api/message-b` — подтверждение обработки сообщения.
- Swagger: http://localhost:10002/swagger/index.html
