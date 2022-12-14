# Продуктовый помощник
![foodgram-project-react workflow](https://github.com/Amica24/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Приложение «Продуктовый помощник» представляет собой сайт, 
на котором пользователи могут публиковать рецепты, добавлять чужие рецепты 
в избранное и подписываться на публикации других авторов. 
Сервис «Список покупок» позволяет пользователям создавать список продуктов, 
которые нужно купить для приготовления выбранных блюд.

Кроме того, для проекта доступны запросы к API. Принцип создания интерфейса - REST, 
переход к API осуществлен на основе Django REST Framework.

Проект доступен по адресу: http://51.250.21.244/recipes

Данные для авторизации в админ-зоне:

логин:
admin
пароль:
admin123

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Amica24/foodgram-project-react.git
```

```
cd foodgram-project-react
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

### Примеры запросов к API:

Запросы к API начинаются с `/api/`


**/users/**

    get:
* Список пользователей.
* Права доступа: Доступно без токена.
  
                page:
                  type: string
                limit:

    
    post:
* Регистрация пользователя.
* Права доступа: Доступно без токена.
  
                email:
                  type: string
                username:
                  type: string
                first_name:
                  type: string
                last_name:
                  type: string
                password:
                  type: string       
                  
                  
**/users/{id}/**

    get:
* Профиль пользователя.
* Права доступа: Аутентифицированные пользователи.
  
                id:
                  type: string    
                  
**/users/me/**

    get:
* Профиль текущего пользователя.
* Права доступа: Аутентифицированные пользователи.

**/users/set_password/**
    
    post:
* Изменение пароля текущего пользователя.
* Права доступа: Аутентифицированные пользователи.
  
                new_password:
                  type: string
                current_password:
                  type: string                                           

**/auth/token/login/** 
    
    post:
* Получения токена авторизации в обмен на password и email.
* Права доступа: Доступно без токена.
  
                password:
                  type: string
                email:
                  type: string
                      
**/auth/token/logout/** 
    
    post:
* Удаление токен текущего пользователя.
* Права доступа: Аутентифицированные пользователи.
  
**/tags/**
  
    get:
* Получить список всех тегов
* Права доступа: Доступно без токена.  

**/tags/{id}/** 
    
    
    get:
* Получить тег
* Права доступа: Доступно без токена.

      params:
      - id
      
**/ingredients/**
  
    get:
* Список ингредиентов с возможностью поиска по имени.
* Права доступа: Доступно без токена. 

      params:
      -name 

**/ingredients/{id}/** 
    
    
    get:
* Получить ингредиент
* Права доступа: Доступно без токена.

      params:
      - id


**/recipes/**


    get:
* Получить список всех рецептов
* Права доступа: Доступно без токена.

       params: 

        - page	
        integer
        
        - limit	
        integer
        
        - is_favorited	
        integer
        
        - is_in_shopping_cart	
        integer
        
        - author	
        integer
        
        - tags


    post:
* Добавить новый рецепт
* Права доступа: Аутентифицированные пользователи.


      required:
        - ingredients
        - tags
        - image
        - name
        - text
        - cooking_time
      properties:
        ingredients:
          type: array of objects
          title: Список ингредиентов
        tags:
          type: array of integers
          title: Список id тегов
        image:
          type: string
          title: Картинка, закодированная в Base64
        name:
          type: string
          title: Название
        text:
          type: string
          title: Описание
        cooking_time:
          type: integer
          title: Время приготовления (в минутах)
          


**/recipes/{id}/**


    get:
* Получение рецепта
* Права доступа: Доступно без токена. 

      params:
      - id


    patch:
* Обновление рецепта
* Права доступа: Автор рецепта, администратор.


    delete:
* Удаление рецепта
* Права доступа: Автор рецепта, администратор.


**/recipes/download_shopping_cart/**


    get:
* Скачать список покупок
* Права доступа: Аутентифицированные пользователи.


**/api/recipes/{id}/shopping_cart/**


    post:
* Добавить рецепт в список покупок
* Права доступа: Аутентифицированные пользователи. 


    delete:
* Удалить рецепт из списка покупок
* Права доступа: Аутентифицированные пользователи.

**/api/recipes/{id}/favorite/**


    post:
* Добавить рецепт в избранное
* Права доступа: Аутентифицированные пользователи. 


    delete:
* Удалить рецепт из избранного
* Права доступа: Аутентифицированные пользователи. 


**/users/subscriptions/**


    get:
* Получить список пользователей, на которых подписан текущий пользователь
* Права доступа: Аутентифицированные пользователи.

**/api/users/{id}/subscribe/**


    post:
* Подписаться на пользователя
* Права доступа: Аутентифицированные пользователи. 


    delete:
* Отписаться от пользователя
* Права доступа: Аутентифицированные пользователи. 
