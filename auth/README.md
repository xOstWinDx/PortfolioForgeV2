
# Сервис Аутентификации

**Сервис Аутентификации** — ключевой компонент микросервисного бэкенда [PortfolioForgeV2](https://github.com/yourusername/PortfolioForgeV2), обеспечивающий безопасную аутентификацию и авторизацию для моего сайта-визитки. Он отвечает за вход пользователей, выдачу JWT и управление ключами, гарантируя безопасность для разделов с проектами, блогом и комментариями.

## Возможности

- **Аутентификация пользователей**: Безопасный вход по логину/паролю с выдачей HttpOnly cookies с JWT (`access_token`, `refresh_token`).  
- **Управление JWT**: Генерация и валидация токенов с использованием RS256, автоматическое обновление токенов.  
- **Эндпоинт JWKS**: Предоставляет публичные ключи по `/.well-known/jwks.json` для проверки токенов.  
- **Ролевой доступ**: Поддержка ролей (`ADMIN`, `USER` и др.) для гибкого управления правами.  

## Технологии

- **Python 3.11** и **FastAPI** для высокопроизводительных API.  
- **Cryptography** для генерации RSA-ключей и подписи JWT.  
- **Docker** для контейнеризации.  
- **Pre-commit** с RUFF и MyPy для качества кода.  

## Начало работы

### Требования
- Python 3.12+  
- Docker (опционально, для контейнеров)  
- `pip` для управления зависимостями  

### Установка
1. Склонируйте репозиторий:  
   ```bash
   git clone https://github.com/yourusername/PortfolioForgeV2.git
   cd PortfolioForgeV2/auth
   ```
2. Установите зависимости:  
   ```bash
   pip install poetry
   ```
   ```bash
   poetry install
   ```

3. Запустите сервис:  
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Docker
```bash
docker-compose up --build
```

## Эндпоинты API
- `POST /register`: Регистрация нового пользователя.
- `POST /login`: Аутентификация пользователя, возвращает `access_token` и `refresh_token` в cookies.  
- `POST /refresh`: Обновление истёкшего `access_token` с помощью `refresh_token`.  
- `GET /.well-known/jwks.json`: Получение публичных ключей для проверки JWT.  


## Разработка

- **Линтинг и форматирование**: Запустите `pre-commit run --all-files` для проверки стиля кода.  
- **Тестирование**: Тесты в `tests/` (в процессе).  
- **Контрибьютинг**: Открывайте issues/PR на [GitHub](https://github.com/yourusername/PortfolioForgeV2).  

## Лицензия

MIT License. См. [LICENSE](LICENSE).  

## Контакты

Создано [xOstWinDx](https://github.com/xOstWinDx) для демонстрации моих навыков бэкенд-разработчика. Пишите на [Starobogatov.a@yandex.ru](mailto:Starobogatov.a@yandex.ru) или в [telegram](https://t.me/m/gyCN5rIrNThi)!
```