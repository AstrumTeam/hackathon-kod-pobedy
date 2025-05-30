# Pobedaletters

Код проекта Pobedaletters. Сайт: https://pobedaletters.ru

Осбенности проекта:

- **БЕЗ API**. Абсолютно все работает локально  
- Сайт поддерживает 11 языков. Пайплайн генерации более 100 языков
- Поддержка пользователей через telegram бот
- Выбор диктора времен Великой Отечесвенной Войны
- Полное покрытие автотестами
- Очередь запросов
- Микросервисная архитектура
- Тестировка API через postman
- Мобильная версия сайта

Осбенности генерации фильма по письму:
- Генерация обложки
- Генерация субтитров
- Фоновая музыка
- Интерполяция видео (Генерация в 32 FPS)
- Динамическая длина видео сцен

# Локальная установка

## Создайте виртуальное окружение

windows: 

```bash
python -m venv venv && venv/Scripts/activate
```

linux:

```bash
python3 -m venv venv && source venv/bin/activate
```

# Telegram bot

Телеграм бот для технической поддержки сайта. Рабочий бот: [@pobedaletters_supportbot](https://t.me/pobedaletters_supportbot)

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
```
.
├── telegram_bot/                # Папка телеграм бота
│   ├── main.py                  # Основной файл бота
│   ├── faq.py                   # файл с частозадаваемыми вопросами
│   ├── requirements.txt         # Зависимости
│   └── .env                     # Конфигурационный файл (нужно создать)
```


# Backend

## Проверка API
1. Бэкэнд работает на нашем сервере, вы уже можете его протестировать.
2. В папке postman_api лежит json файл примеров запросам к API.
3. Его нужно импортировать в Postman, это позволит вам протестировать API.

Далее следуют инструкции, для локального запуска. Для запуска вам надо будет установить PostgreSQL на сервер.

## Установка

1. Установите зависимости:
```bash
pip install -r backend/requirements.txt
```

2. Чтобы модель Text-To-Speech работала нужно скачать веса

```bash
huggingface-cli download "TVI/f5-tts-ru-accent" --local-dir "backend\api\modules\f5_ckpt"
```
3. Для интерполяции видео мы используем RIFE

```bash
git clone git@github.com:megvii-research/ECCV2022-RIFE.git "backend\api\modules"
```


## Запуск
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

## Структура проекта
```
.
├── backend/                                # Исходный код
│   ├── api/                                # Утилит
│   │   ├── modules/                        # Каталог основных модулей
│   │   │   ├── speakers/                   # сэмплы дикторов
│   │   │   ├── songs/                      # фоновая музыка
│   │   │   ├── llm_module.py               # Модуль с LLM
│   │   │   ├── main_service.py             # Главный модуль с методом генерации
│   │   │   ├── music_module.py             # Модуль подбора и обрезки музыки
│   │   │   ├── norm_module.py              # Модуль нормализации письма 
│   │   │   ├── stt_module.py               # Модуль создания субтитров
│   │   │   ├── tts_module.py               # Модуль озвучки письма
│   │   │   ├── text2image_module.py        # Модуль создания обложки видео
│   │   └── └── text2video_module.py        # Модуль создания кадров видео
│   │   ├── views.py                        # REST API и обработка запросов, очередь запросов
│   │   ├── tests.py                        # Автотесты
│   │   ├── models.py                       # Data-классы таблиц из бд
└── └── └── serializers.py                  # Сериализаторы
```

# Frontend

## Проверка UI
1. Фронтенд можно запустить локально и протестировать через браузер.
2. Для работы требуется установленный Node.js (желательно LTS 18.x) и Angular CLI.

---

## Установка

1. Установите Angular CLI, если он не установлен:

```bash
npm install -g @angular/cli
```

2. Установите зависимости проекта:

```bash
cd frontend
npm install
```

---

## Запуск проекта

```bash
ng serve
```

После запуска фронтенда откройте браузер и перейдите по адресу:

```
http://localhost:4200/
```

---

## Структура проекта
```
.
├── frontend/                # Папка телеграм бота
│   ├── src/
│   │   ├── app/             # компоненты и логика приложения
│   │   └── asserts/         # изображения и статические файлы
│   ├── angular.json         # конфигурация Angular CLI
│   └── package.json         # зависимости и npm-скрипты
```

---

## Примечание

Папка `node_modules` не хранится в репозитории. После клонирования проекта обязательно выполните `npm install`, чтобы восстановить все зависимости.

Angular CLI версии: `15.1.6`  
Node.js версии: `20.16.0` (рекомендуется использовать LTS 18.x)