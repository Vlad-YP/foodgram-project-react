![example workflow](https://github.com/Vlad-YP/foodgram-project-react/workflows/foodgram_workflows.yml/badge.svg)

# Foodgram - «Продуктовый помощник»

На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Адрес и данные для проверки
base - http://84.201.162.208/

Обычный пользователь:
- povar@povar.com
- 111111part

Суперузер:
- admin_boss
- 12345678

## Как запустить проект:

1. Создать в /infra файл .env
Шаблон заполнения:

```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_HOST=
DB_PORT=

SECRET_KEY=
ALLOWED_HOSTS=
DEBUG=
```

2. Запуск docker-compose

```
docker-compose up -d --build 
```

3. Выполнить по очереди команды:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```

В проекте есть mangment-команда с ингридиентами:

```
docker-compose exec backend python manage.py add_ingredients
```

файл с данными лежит в /backend/data/

## CI и CD
- Тестирование на flake8
- Отправка образа foodgram_backend на https://hub.docker.com/
- Деплой на сервер с подготовкой проекта(создание env, выполнение manage-команд)
- Отправка сообщения в телеграм

## Примеры запросов:
К проекту подключен модуль redoc, содержащий документацию по доступным эндпоинтам и примерам запросов. Адрес для redoc - [base]/redoc/.

## Пользователи 

### login [POST]
```
/auth/token/login/
```
    {
        "password": "12345678",
        "email": "admin@admin.ru"
    }

### logout [POST]
```
/auth/token/logout/
```

### Список пользователей [GET]
```
/api/users/
```
Структура ответа:

    {
    "count": 123,
    "next": "http://foodgram.example.org/api/users/?page=4",
    "previous": "http://foodgram.example.org/api/users/?page=2",
    "results": [
        {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
        }
    ]
    }

### Регистрация пользователя [POST]
```
/api/users/
```
    {

    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Q4fgdfg34"

    }


### Профиль пользователя [GET]
```
/api/users/{id}/
```

### Текущий пользователь [GET]
```
/api/users/me/
```

### Изменение пароля [POST]
```
/api/users/set_password/
```
    {

        "new_password": "123456789",
        "current_password": "12345678"

    }

### Мои подписки [GET]
```
/api/users/subscriptions/
```
Структура ответа:

    {
    "count": 123,
    "next": "http://foodgram.example.org/api/users/subscriptions/?page=4",
    "previous": "http://foodgram.example.org/api/users/subscriptions/?page=2",
    "results": [
        {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": true,
        "recipes": [
            {
            "id": 0,
            "name": "string",
            "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
            "cooking_time": 1
            }
        ],
        "recipes_count": 0
        }
    ]
    }

### Подписаться на пользователя [POST]
```
/api/users/{id}/subscribe/
```


## Ингредиенты

### Список ингредиентов [GET]
```
/api/ingredients/?name=абрикос
```

Ответ:

    [
        {
            "id": 0,
            "name": "Капуста",
            "measurement_unit": "кг"
        }
    ]

### Получение ингредиента [GET]
```
/api/ingredients/{id}/
```

## Теги

### Cписок тегов [GET]
```
/api/tags/
```
Ответ:

    [
        {
            "id": 0,
            "name": "Завтрак",
            "color": "#E26C2D",
            "slug": "breakfast"
        }
    ]

### Получение тега [GET]
```
/api/tags/{id}/
```

## Рецепты

### Список рецептов [GET]
```
/api/recipes/
```
Ответ:

    {
        "count": 123,
        "next": "http://foodgram.example.org/api/recipes/?page=4",
        "previous": "http://foodgram.example.org/api/recipes/?page=2",
        "results": [
            {
            "id": 0,
            "tags": [
                {
                "id": 0,
                "name": "Завтрак",
                "color": "#E26C2D",
                "slug": "breakfast"
                }
            ],
            "author": {
                "email": "user@example.com",
                "id": 0,
                "username": "string",
                "first_name": "Вася",
                "last_name": "Пупкин",
                "is_subscribed": false
            },
            "ingredients": [
                {
                "id": 0,
                "name": "Картофель отварной",
                "measurement_unit": "г",
                "amount": 1
                }
            ],
            "is_favorited": true,
            "is_in_shopping_cart": true,
            "name": "string",
            "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
            "text": "string",
            "cooking_time": 1
            }
        ]
    }

### Создание рецепта [POST]
```
/api/recipes/
```

    {
        "ingredients": [
            {
            "id": 2,
            "amount": 10
            },
            {
            "id": 3,
            "amount": 10
            }
        ],
        "tags": [
            1,
            2
        ],
        "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
        "name": "string",
        "text": "string",
        "cooking_time": 1
    }

### Получение рецепта [GET]
```
/api/recipes/{id}/
``` 

### Обновление рецепта [PATCH]
```
/api/recipes/{id}/
```

### Удаление рецепта [DELETE]
```
/api/recipes/{id}/
```

## Список покупок

### Скачать список покупок [GET]
```
/api/recipes/download_shopping_cart/
```
Ответ - text/plain

### Добавить рецепт в список покупок [POST]
```
/api/recipes/{id}/shopping_cart/
```

### Удалить рецепт из списка покупок [POST]
```
/api/recipes/2/shopping_cart/
```

## Избранное

### Добавить рецепт в избранное [POST]
```
/api/recipes/{id}/favorite/
```
Ответ:

    {
    "id": 0,
    "name": "string",
    "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
    "cooking_time": 1
    }

### Удалить рецепт из избранного [DELETE]
```
/api/recipes/{id}/favorite/
```


## Авторы

- Команда Яндекс.Практикум
- Владислав Максимов(студент)