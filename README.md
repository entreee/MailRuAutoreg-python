# Описание проекта "MailRuAutoreg-python"

Этот проект представляет собой автоматизированный скрипт на Python для регистрации аккаунтов на почтовом сервисе Mail.ru. С помощью данного скрипта можно создавать новые аккаунты в автоматическом режиме.

## Использование

### Подготовка

1. Установите необходимые зависимости, выполнив команду:
`pip install -r requirements.txt`
2. Зарегистрируйте аккаунт на сервисе [rucaptcha.com](https://rucaptcha.com) и получите API ключ.

3. Отредактируйте файл `config.ini` с настройками:
```ini
[token]
key = ваш_ключ_от_rucaptcha

[settings]
session_count = количество_сессий_регистрации
headless = True/False
```
`session_count` - количество параллельных сессий регистрации.headless - флаг для запуска браузера в headless режиме (без GUI).

`headless` - флаг для запуска браузера в headless режиме (без GUI).

## Запуск

1. Запустите скрипт `MailRuAutoreg.py`.
2. Следуйте инструкциям для регистрации аккаунтов.

## Файлы

- `MailRuAutoreg.py`: основной скрипт для регистрации аккаунтов.
- `config.ini`: файл с настройками.
- `requirements.txt`: список зависимостей.

## Требования к окружению

- Python 3.x

## Зависимости

- `configparser==6.0.1`
- `attrs==23.2.0`
- `requests==2.31.0`
- `selenium==4.19.0`
- `loguru==0.7.2`

## Ссылки

Репозиторий проекта на GitHub: [MailRuAutoreg-python](https://github.com/entreee/MailRuAutoreg-python)
