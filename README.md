# [1С:Предприятие. Облачная подсистема Фреш](https://v8.1c.ru/tekhnologii/1cfresh/o-tekhnologii/ "1C:Enterprise. Cloud Subsystem Fresh") в Docker

[![Docker](https://img.shields.io/badge/Docker-ready-green.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3+-yellow.svg)](https://www.python.org/)
[![1C:Fresh](https://img.shields.io/badge/1C%3AFresh-cloud-red.svg)](https://v8.1c.ru/tekhnologii/1cfresh/)

> Позволяет в течение **~30 минут** развернуть рабочий стенд облачной подсистемы Фреш с использованием технологии Docker.

## 🎯 Для чего это нужно

- 🛠 **Разработка** конфигураций, работающих в облаке
- 🔬 **Разработка** самой технологии Fresh
- 🧪 **Тестирование** средств адаптации конфигураций
- 📋 **Централизованное** управление информационными базами
- 🔄 **Планирование и выполнение** обновлений
- 👥 **Завершение работы** пользователей удалённо

---

## 📋 Содержание

1. [Системные требования](#1-системные-требования)
2. [Структура проекта](#2-структура-проекта)
3. [Подготовка к развертыванию](#3-подготовка-к-развертыванию)
4. [Лицензирование](#4-лицензирование)
5. [Быстрый старт](#5-быстрый-старт)
6. [Подробное описание шагов](#6-подробное-описание-шагов)
7. [Настройка hosts](#7-настройка-файла-hosts)
8. [Доступ к компонентам](#8-адреса-для-доступа-к-компонентам-стенда)
9. [Управление стендом](#9-управление-стендом)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Системные требования

| Ресурс | Минимум | Рекомендовано |
|--------|---------|---------------|
| **Оперативная память** | 12 ГБ | 16 ГБ |
| **Свободное место** | 50 ГБ | 100 ГБ |
| **ОС** | Linux, macOS, Windows | Ubuntu 20.04+ |

### Необходимое ПО

- [**Python 3+**](https://www.python.org/downloads/)
- [**Docker** — инструкция по установке](https://docs.docker.com/engine/install/)
- [**Docker Compose** — инструкция по установке](https://docs.docker.com/compose/install/)

### Python-зависимости

```bash
pip install -r requirements.txt
```

Зависимости: `requests`, `beautifulsoup4`.

> ⚠️ **macOS:** Используйте Docker VMM в качестве менеджера ВМ (Settings → General → Virtual Machine Options) для корректной сборки образов.

### Linux: запуск docker без sudo

```bash
sudo usermod -aG docker ${USER}
# После этого перезайдите в сессию
```

---

## 2. Структура проекта

```
docker_fresh/
├── deploy.py                    # Главный скрипт (скачать → собрать → развернуть)
├── download_releases.py         # Скачивание дистрибутивов 1C с releases.1c.ru
├── install.py                   # Сборка Docker-образов
├── start.py                     # Развертывание и запуск стенда
├── components_config.py         # Конфигурация компонентов
├── docker-compose_pattern.yml   # Шаблон docker-compose
├── requirements.txt             # Python-зависимости
├── README.md                    # Эта справка
│
├── modules/                     # Модули для сборки образов
│   ├── core.py                  # Базовые функции Docker
│   ├── debian.py                # Образы на базе Debian
│   ├── centos.py                # Образы на базе CentOS
│   ├── cs.py                    # Система взаимодействия
│   ├── esb.py                   # 1С:Шина
│   ├── gate.py                  # Шлюз приложений
│   ├── site.py                  # Веб-сайт Fresh
│   ├── forum.py                 # Форум Fresh
│   ├── db.py                    # PostgreSQL для db
│   └── helper.py                # Вспомогательные функции
│
├── distr/                       # Дистрибутивы (заполняется автоматически)
│                              # Создаётся при запуске download_releases.py
│
├── conf/                        # Конфигурации сервисов
│   ├── core/                    # Конфигу fresh/core
│   │   ├── conf.cfg             # Конфигурация ядра
│   │   ├── logcfg.xml           # Логирование
│   │   └── nethasp.ini          # Лицензирование netHASP
│   ├── forum/                   # Конфигурация Tomcat (Forum)
│   │   ├── context.xml
│   │   └── server.xml
│   ├── nginx/                   # Конфигурация Nginx
│   │   ├── 1c_*.conf            # Фрагменты конфигурации 1C
│   │   ├── nginx.conf
│   │   └── conf.d/              # Включаемые конфиги
│   └── site/                    # Конфигурация Tomcat (Site)
│       ├── context.xml
│       └── server.xml
│
├── certs/                       # SSL-сертификаты
├── licenses_1c/                 # Папка для лицензий 1C (создаётся при деплое)
├── images/                      # Собранные Docker-образы
├── other_files/                 # Вспомогательные файлы
│   ├── fresh_components.json    # Компоненты Fresh
│   ├── params.json              # Список ИБ для создания
│   ├── cfe/                     # .cfe файлы (УправлениеМС, API)
│   ├── psql-scripts/            # SQL для создания БД
│   └── vrd/                     # VRD-файлы (лицензии, OpenID, сессии)
│
└── workdir/                     # Создаётся при запуске (runtime, docker-compose.yml)
```

> ⚠️ **Примечание:** Папка `distr/` заполняется автоматически скриптом `download_releases.py` при наличии доступа к `releases.1c.ru`.

---

## 3. Подготовка к развертыванию

### Дистрибутивы

Все необходимые дистрибутивы скачиваются автоматически при наличии доступа к `releases.1c.ru`.

| Компонент | Версия | Источник |
|-----------|--------|----------|
| Платформа 1C Предприятие 8.3 | последняя | [releases.1c.ru](https://releases.1c.ru/project/Platform83) |
| Сайт Fresh | последняя | [FreshPublic](https://releases.1c.ru/project/FreshPublic) |
| Форум Fresh | последняя | [FreshPublic](https://releases.1c.ru/project/FreshPublic) |
| Шлюз приложений | последняя | [FreshPublic](https://releases.1c.ru/project/FreshPublic) |
| Менеджер сервиса | последняя | [FreshPublic](https://releases.1c.ru/project/FreshPublic) |
| Агент сервиса | последняя | [FreshPublic](https://releases.1c.ru/project/FreshPublic) |
| 1С:Библиотека технологии сервиса | 2.0+ | [SMTL20](https://releases.1c.ru/project/SMTL20) |

### ⚠️ Безопасность

Данный стенд по умолчанию использует домен `1cfresh-dev.ru` и сертификаты Let's Encrypt **только для тестирования**.

Для production:
1. Замените домен `1cfresh-dev.ru` на свой в файле `start.py`
2. Разместите ваши SSL-сертификаты в каталоге `certs/`

### Клонирование репозитория

```bash
git clone https://github.com/1C-Company/docker_fresh.git
cd docker_fresh
```

### Настройка информационных баз

Файл [`other_files/params.json`](other_files/params.json) содержит параметры развертывания:

| Поле | Описание |
|------|----------|
| `ИмяХоста` | Имя хоста (заменяется скриптом на `HOSTNAMEREPLACE`) |
| `ИнформационныеБазы[]` | Массив информационных баз |

**Параметр одной ИБ:**

| Поле | Описание |
|------|----------|
| `Сервер` | Сервер публикации (напр. `web/int/sm`) |
| `ИмяВКластере` | Имя в кластере |
| `КодКонфигурации` | Код конфигурации |
| `ТипКонфигурации` | Тип: Управляющая / Прикладная / Сервисная |
| `Администратор` | Имя пользователя-администратора |
| `ПользовательУправления` | Пользователь для управления |
| `ИмяВнешнейПубликации` | Имя внешней публикации |
| `ИмяВнутреннейПубликации` | Имя внутренней публикации |
| `ИмяФайлаШаблонаВнешнейПубликации` | Шаблон внешней публикации (zoneless / withzone) |
| `ИмяФайлаШаблонаВнутреннейПубликации` | Шаблон внутренней публикации |
| `СоздаватьВМенеджере` | Создавать в менеджере сервисов |
| `ИмяФайлаКонфигурации` | Имя `.cf` файла (из `distr/`) |
| `БлокироватьРаботуРегЗаданийПриСоздании` | Блокировка рег. заданий при создании |

> ⚠️ **Первая база в списке должна создаваться в менеджере (`СоздаватьВМенеджеру: true`)!**

Реальные данные из файла (4 ИБ по умолчанию): `SM` → `SMTL` → `SA` → `AM`.

---

## 4. Лицензирование

Стенд требует два типа лицензий:

| Тип | Описание |
|-----|----------|
| **Серверная** | Для сервера 1C:Enterprise |
| **Клиентская** | Для каждого подключившегося клиента |

### Если лицензии уже имеются

В случае, если лицензии уже активированы (проброшены HASP-ключи, активированы программные лицензии или настроен сервер лицензирования), можно **сразу переходить к пункту [Быстрый старт](#5-быстрый-старт)**.

### Если лицензии отсутствуют

Для лицензирования необходимо собрать образ `fresh/core`, который содержит утилиту `ring` для активации программных лицензий 1C:Enterprise.

**Порядок действий:**

#### Шаг 1: Сборка образа fresh/core

```bash
python3 install.py
```

> ⚠️ Образ `fresh/core` собирается автоматически на этапе `install.py`. Это необходимо выполнить **до активации лицензий**.

#### Шаг 2: Активация лицензий (один из вариантов)

##### Вариант A: Проброс HASP ключей

В `docker-compose.yml` монтируется `/tmp/.aksusb` в контейнер `srv`:

```yaml
services:
  srv:
    volumes:
      - /tmp/.aksusb:/tmp/.aksusb
```

Установите драйвер HASP по ссылке: [Thales HASP Drivers](https://supportportal.thalesgroup.com/csm?id=kb_search&query=kbcat_drivers_%26_runtime_packages)

##### Вариант B: Программные лицензии через `ring`

```bash
docker run -it --rm --hostname srv.newstand.1cfresh-dev.ru \
  -v ./licenses_1c:/var/1C/licenses \
  fresh/core bash -l -c 'JAVA_HOME=/opt/1cv8/x86_64/8.5.1.1302/jre \
  /opt/1C/1CE/components/1c-enterprise-ring-0.20.0+4-x86_64/ring \
  license activate --first-name "Ivan" \
    --last-name "Ivanov" \
    --email "ivan@example.com" \
    --country "Russia" \
    --serial "XXXX-XXXX" \
    --pin "12345678"'
```

##### Вариант C: Сервер лицензирования

Отредактируйте `conf/core/nethasp.ini`:

```ini
; Раскомментируйте и укажите сервер
ServerName=license-server.local
```

---

## 5. Быстрый старт

```bash
# Полный цикл: скачать → собрать → развернуть
python3 deploy.py -new -h mystandname
```

### Параметры deploy.py

| Флаг | Описание |
|------|----------|
| `-h <имя_хоста>` | **Обязательный.** Имя хоста для стенда |
| `-new` | Развернуть **новый** стенд |
| `-debug` | Подробный вывод в терминал |
| `--skip-download` | Пропустить скачивание дистрибутивов |
| `--skip-install` | Пропустить сборку Docker-образов |

### Примеры использования

```bash
# Полный цикл с новым стендом
python3 deploy.py -new -h mytest

# Развернуть с подробным выводом
python3 deploy.py -new -h mytest -debug

# Только развёртывание (пропустив скачивание и сборку)
python3 deploy.py -h mytest --skip-download --skip-install
```

---

## 6. Подробное описание шагов

### Шаг 1: Скачивание дистрибутивов

```bash
python3 download_releases.py
```

При запуске предлагается указать версии компонентов или принять значения по умолчанию.

> ⚠️ Полноценная работа не гарантирована при изменении значений по умолчанию.

### Шаг 2: Сборка Docker-образов (8 образов)

| Образ | Назначение |
|-------|-----------|
| `debian` | Базовый образ для `core` и `db` |
| `core` | Платформа 1C, клиентская и серверная часть + ring, onescript |
| `db` | PostgreSQL — сервер баз данных |
| `site` | Веб-сайт Fresh |
| `forum` | Форум Fresh |
| `gate` | Шлюз приложений Fresh |
| `cs` | Система взаимодействия |
| `esb` | 1С:Шина |

```bash
python3 install.py [-debug]
```

### Шаг 3: Развертывание стенда (11 контейнеров)

При запуске создаются следующие контейнеры:

| Контейнер | Связанное изображение |
|-----------|----------------------|
| `db` | fresh/db |
| `srv` | fresh/core (1C Server) |
| `ras` | fresh/core (Runtime Agent Server) |
| `web` | fresh/esb (Шина + веб-маршрутизация) |
| `gate` | fresh/gate |
| `s3` | fresh/gate (S3-хранилище) |
| `cs` | fresh/cs |
| `esb` | fresh/esb |
| `nginx` | fresh/site (обратный прокси) |
| `site` | fresh/site (основное приложение) |
| `forum` | fresh/forum |

#### Создание нового стенда

```bash
python3 start.py -new -h <имя>
```

Параметр `-h` задаёт адрес стенда:
- `mystand` → `https://mystand.1cfresh-dev.ru`
- Контейнер сервера: `srv.mystand.1cfresh-dev.ru`

> 📁 Файл `.hostname` создаётся автоматически при `-new`. Последующие запуски без `-new` читают его для восстановления имени хоста.

#### Повторный запуск существующего стенда

```bash
python3 start.py
```

---

## 7. Настройка файла hosts

Для доступа к веб-клиентам, конфигурациям и API:

```bash
# Добавьте строку в /etc/hosts (macOS/Linux) или C:\Windows\System32\drivers\etc\hosts (Windows)
192.168.1.6 mystandname.1cfresh-dev.ru srv.mystandname.1cfresh-dev.ru s3.1cfresh-dev.ru
```

> 🔍 **WSL2:** Получить IP в WSL2:
> ```bash
> ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
> ```

---

## 8. Адреса для доступа к компонентам стенда

| Компонент | URL |
|-----------|-----|
| 🌐 **Сайт Fresh** | `https://mystandname.1cfresh-dev.ru` |
| 📊 **Менеджер сервиса (веб)** | `https://mystandname.1cfresh-dev.ru/a/adm?Oid=-` |
| 🔧 **Конфигуратор** | `Srvr="srv.mystandname.1cfresh-dev.ru";Ref="<имя_ИБ>";` |

Имена ИБ берутся из `other_files/params.json`.

---

## 9. Управление стендом

### Запуск
```bash
python3 deploy.py -new -h myhost
```

### Остановка
```bash
cd workdir
docker-compose down
```

### Просмотр логов
```bash
cd workdir
docker-compose logs -f
```

### Перезагрузка
```bash
cd workdir
docker-compose restart
```

---

## 10. Troubleshooting

### Проблема: Docker не запускается без sudo

```bash
sudo usermod -aG docker ${USER}
# Перезайдите в сессию!
newgrp docker
```

### Проблема: Ошибка скачивания дистрибутивов

Проверьте доступ к `releases.1c.ru` и наличие интернет-соединения.

### Проблема: SSL-сертификаты

Для production замените сертификаты в `certs/` на свои.

### Проблема: Доступ по HTTP не работает

Убедитесь, что IP в `/etc/hosts` совпадает с вашим сервером.

### Проблема: Не хватает памяти

Минимум 4 ГБ, но рекомендуется 8 ГБ для стабильной работы.

### Проблема: Ошибка сборки образов на macOS

```
Settings → General → Virtual Machine Options → Use VMM
```

## 📞 Поддержка

- [GitHub Issues](https://github.com/1C-Company/docker_fresh/issues)
- [Документация 1C:Fresh](https://v8.1c.ru/tekhnologii/1cfresh/)