# Wallet API — управление кошельками

Асинхронное REST API для управления кошельками с историей операций и веб-интерфейсом.  
Проект запускается через Docker Compose и включает три сервиса: базу данных, бэкенд (FastAPI) и фронтенд (Nginx).

---

## Быстрый старт

Клонируйте репозиторий:
   
   git clone https://github.com/yourusername/wallet-api.git
   
Запустите все контейнеры:


docker-compose up -d --build

Откройте в браузере:

Веб-интерфейс: http://localhost (порт 80)

API документация: http://localhost:8000/docs

## Технологии
Backend: Python 3.12, FastAPI, SQLAlchemy (async), Alembic

Database: PostgreSQL 16

Frontend: Nginx, HTML, JavaScript

Infrastructure: Docker, docker-compose

Testing: pytest, pytest-asyncio, httpx


## API Endpoints
POST /api/v1/wallets/{wallet_uuid}/operation
Выполнить операцию (пополнение / снятие).

Пример запроса:

json
{
  "operation_type": "DEPOSIT",
  "amount": 100.50
}
Пример ответа:

json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "balance": 100.50,
  "transactions": [
    {
      "id": 1,
      "operation_type": "DEPOSIT",
      "amount": 100.50,
      "timestamp": "2026-03-25T12:00:00"
    }
  ]
}
GET /api/v1/wallets/{wallet_uuid}
Получить текущий баланс.
Параметр include_history=true добавляет последние 10 операций.

## Переменные окружения

Создайте .env из .env.example

## Запуск тестов

docker-compose exec app pytest tests/

## Примечания
Кошелёк создаётся автоматически при первом пополнении.

Снятие средств невозможно, если баланс недостаточен (ошибка 400).

Все операции записываются в таблицу transactions.

Конкурентные запросы на один кошелёк обрабатываются корректно благодаря блокировке строк SELECT ... FOR UPDATE.