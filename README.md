# API-сервис сокращения ссылок

## Описание проекта

Этот проект представляет собой API-сервис для сокращения ссылок, который позволяет пользователям создавать короткие URL-адреса, управлять ими и отслеживать статистику переходов.

## Как это работает

Пользователь отправляет POST-запрос на создание короткой ссылки, и сервис генерирует уникальный короткий код для данной ссылки. 
При переходе по короткому URL пользователь будет перенаправлен на оригинальный длинный URL. 

## Функционал сервиса

### Функции
![image](https://github.com/user-attachments/assets/7346b1a1-3442-46be-af62-1dcbd5fff7a9)

   - **POST /links/shorten** - создаёт короткую кастомную ссылку, с передачей параметров `short_code` - для создания кастомной ссылки и `expires_at` для указания даты удаления ссылки
   - **GET /links/{short_code}** - перенаправляет на оригинальный URL.
   - **DELETE /links/{short_code}** - удаляет связь.
   - **PUT /links/{short_code}** - обновляет URL, удаляя старый short_code и заменяет его новым.
   - **GET /links/{short_code}/stats** - отображает оригинальный URL, дату создания, количество переходов и дату последнего использования.
   - **GET /links/search?original_url={url}** - осуществляет поиск ссылки по оригинальному URL

### Регистрация
Изменение и удаление ссылок доступны только зарегистрированным пользователям. Зарегистрированные пользователи могут удалять и изменять только свои ссылки. 

### База данных и кэширование
Для хранения ссылок и информации о пользователи была развернута база данных postgresql, которая содержит две таблицы:
- Users
![image](https://github.com/user-attachments/assets/b3ceabab-80f7-45a2-87d9-42fa250ce410)
- Links
![image](https://github.com/user-attachments/assets/1b1d5fae-f62c-455b-a2e6-e223e4d1edd0)

Для управления версиями базы данных использовалась библиотека alembic. Для работы над объектами из базы данных в питоне использовалась библиотека sqlalchemy.

### Кэширование
Для кеширования наиболее частых запросов в приложении используется библиотека cachetools. В приложении я кеширую до 32 ссылок, которые использовались более 5 раз и не удалены. Счетчик количества перехода по ссылке осуществляется в методе **GET /links/{short_code}**.

## Примеры запросов

1. Создание короткой ссылки
   ```
   POST /links/shorten
   {
       "long_url": "[https://example.com](https://dashboard.render.com/web/srv-cvg6j83v2p9s73dif5qg/logs)",
       "custom_alias": "test1111",
       "expires_at": "2025-03-29 23:59"
   }
   ```
   Ответ:
   ![image](https://github.com/user-attachments/assets/9c88188f-cea0-42ef-b47b-652db01d3a01)

   После перехода по ссылке в базе данных увеличивается параметр number_of_click и изменяется date_use
   ![image](https://github.com/user-attachments/assets/51f93e68-614c-4f09-af24-ccfd18ceb1ed)


3. Получение статистики по ссылке
   ```
   GET /links/{short_code}/stats
   ```
   Пример ответа:
   
   ![image](https://github.com/user-attachments/assets/83389149-8f22-445c-9eef-d807bf8bda3f)


5. Поиск ссылки по оригинальному URL
   ```
   GET /links/search/full_url
   {
       "url": "https://github.com/AI-DevTools24/base-5-6-fastapi-Maksim-de/blob/main/main.py",
   }
   ```
   ![image](https://github.com/user-attachments/assets/65e0f249-99ad-4190-bc0a-e6555e44929b)

## Инструкция по запуску

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/Maksim-de/FastApi_short_url.git
   ```
   
2. Настройте окружение проекта. Создайте файл .env и заполните его следующими атрибутами::
   ```
   
   DB_USER = 
   DB_PASS = 
   DB_HOST = 
   DB_PORT = 
   DB_NAME = 
   BASE_URL = 
   SECRET = 
   ```
Для работы сервиса требуется развернутый postgresql. 
3. Запустите сервис:
   ```
   docker build -t my-fastapi-app .
   docker run -p 8000:8000 my-fastapi-app
   ```

Теперь сервис должен быть доступен на `http://localhost:8000`.

