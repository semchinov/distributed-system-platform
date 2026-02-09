# Service A (Python, FastAPI)
#### (by Mikhail on Python FastAPI)

Python-реализация сервиса A, функционально эквивалентная `Example/ServiceA` на C#.
Сервис принимает входящие сообщения, вызывает Service B и отдаёт метрики/трейсы
через OpenTelemetry.

## Требования
- Python 3.12+
- Poetry
- Docker (опционально, для контейнерного запуска)

## Конфигурация
Настройки читаются из переменных окружения (см. `.env.example`):

| Переменная | Значение по умолчанию | Описание |
| --- | --- | --- |
| `SERVICE_NAME` | `service-a` | Имя сервиса для телеметрии |
| `SERVICE_B_URL` | `http://service-b` | Базовый URL сервиса B |
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
docker build -t service-a-python .
docker run --rm -p 10001:80 --env-file .env service-a-python
```

## API
- `POST /api/message-a` — вызывает Service B по `/api/message-b`.
- `POST /api/error?code=500` — возвращает HTTP статус, переданный в `code`.
- Swagger: http://localhost:10001/swagger/index.html
