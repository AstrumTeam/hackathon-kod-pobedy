# hackathon-kod-pobedy



# Telegram bot

Телеграм бот для технической поддержки сайта.

## Установка

1. Установите зависимости:
```bash
pip install -r telegram_bot/requirements.txt
```

2. Создайте файл `.env` и добавьте следующие переменные:
```
BOT_TOKEN=ваш_токен
SUPPORT_CHAT_ID=id_группы
```

## Настройка

1. Получите токен бота у [@BotFather](https://t.me/BotFather) в Telegram
2. Создайте группу для поддержки и добавьте туда бота
3. Получите ID группы поддержки
4. Замените значения в файле `.env`

## Запуск

```bash
python telegram_bot/main.py
```

## Функциональность

- `/start` - Начало работы с ботом
- `/help` - Получение справки
- `/faq` - список частозадаваемых вопросов
- Любое текстовое сообщение будет отправлено команде поддержки

## Структура проекта

- `main.py` - Основной файл бота
- `faq.py` - файл с частозадаваемыми вопросами
- `requirements.txt` - Зависимости проекта
- `.env` - Конфигурационный файл (нужно создать) 


# Backend

## Проверка API
1. Бэкэнд работает на нашем сервере, вы уже можете его протестировать.
2. В папке postman_api лежит json файл примеров запросам к API.
3. Его нужно импортировать в Postman, это позволит вам протестировать API.

Далее следуют инструкции, для локального запуска.

## Установка

1. Установите зависимости:
```bash
pip install -r backend/requirements.txt
```
2. Чтобы модель Text-To-Speech работала нужно скачать веса

```bash
huggingface-cli download "TVI/f5-tts-ru-accent" --local-dir "backend\api\modules\f5_ckpt"
```

## Запуск
```bash
.\.venv312\Scripts\activate
cd backend
python manage.py runserver 0.0.0.0:8000
```