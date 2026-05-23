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
- `POST /api/message-b` — принимает сообщение с идемпотентностью.
  - **Требуемый header:** `X-Message-Id` (UUID идентификатор сообщения).
  - При отсутствии `X-Message-Id` возвращает HTTP 400 и НЕ обрабатывает запрос.
  - При первом получении `message_id`: выполняет бизнес-логику, сохраняет результат и возвращает JSON-ответ.
  - При повторном получении того же `message_id` (дубле): НЕ выполняет бизнес-логику повторно, возвращает ранее сохранённый результат.
  - В обоих случаях возвращает HTTP 200 и инкрементирует счётчик доставки.
- `POST /api/error?code=500` — возвращает HTTP статус, переданный в `code`.
- Swagger: http://localhost:10002/swagger/index.html

## Метрики
- Экспортируется OpenTelemetry метрика (Meter counter): `delivery_messages_received_total`
  - labels/attributes: `service_name` (значение `service-b` по умолчанию), `message_id` (UUID)
  - **Важно:** счётчик инкрементируется на каждый валидный HTTP-приём (включая дубли), что позволяет отслеживать повторные доставки.

## Идемпотентность
- ServiceBMP хранит обработанные `message_id` в памяти (in-memory dict).
- Используется `asyncio.Lock` для обеспечения thread-safe обработки параллельных запросов.
- При рестарте контейнера хранилище очищается (для данной лабораторной это допустимо).
- Бизнес-логика выполняется только один раз на `message_id`, обеспечивая exactly-once processing (при условии что отправитель делает retry с тем же `message_id`).

