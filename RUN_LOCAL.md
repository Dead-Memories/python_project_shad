# Локальный запуск проекта

Этот файл содержит пошаговую инструкцию по локальному запуску проекта, проверке его работоспособности и остановке.

## При первом запуске:

### 1. Что нужно для запуска

Перед началом работы должны быть установлены:

- Git
- Python 3.12+
- VS Code 
- Docker Desktop или локально установленный PostgreSQL.

### 2. Клонирование проекта

Если нужно забрать проект из ветки:

```bash
git clone --branch fourth_lection --single-branch https://github.com/bekaryukovmv/shad_fastapi_project_2026.git
cd shad_fastapi_project_2026
```

### 3. Открытие проекта

Из корня проекта выполнить команду: ```code .```

### 4. Создать виртуальное окружение

```
python3 -m venv .venv
source .venv/bin/activate
```

### 5. Установить зависимости

```
pip install -r requirements.txt
```

### 6. Настроить переменные окружения

```
cp .env_example .env
```
Проверить, что в .env указаны параметры покдлючения к базам данных.


### 7. Запустить базу данных через Docker

Перед выполнением команды открыть Desktop приложение Docker, а затем выполнить команду:

```
docker compose up -d db
```
Проверить, что контейнер запущен: 
```
docker compose ps
```
## 8. Запустить приложение

Запустить приложение из корня проекта:
```
uvicorn src.main:app --reload
```

### 9. Проверка работоспособности приложения 

1) Открыть в браузере http://127.0.0.1:8000/docs
2) Через тесты pytest -v src/tests
3) Отправив запрос через Postman 


### 10. Остановка приложения 

1) Нажать в терминале Ctrl + C
2) Остановить контейнер docker compose down

## При последующих запусках: 

Запуск 
1. source .venv/bin/activate
2. docker compose up -d db
3. uvicorn src.main:app --reload

Остановка
1. Ctrl + C
2. docker compose down