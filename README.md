


## Стек

Fastapi
Postgres
alembic

redis - кеш
jinja + html + bootstrap

### 5️⃣  Створення міграцій
Автоматичне створення міграцій

`alembic revision --autogenerate -m "create users table"`
Це створить файл у alembic/versions/, де Alembic зафіксує зміни у структурі таблиць.

Перевіряй згенеровані міграції вручну перед застосуванням!

### 6️⃣  Застосування міграцій

```bash
alembic upgrade head
```