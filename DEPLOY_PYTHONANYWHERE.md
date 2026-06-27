# Деплой django-fitness на PythonAnywhere

Гайд для бесплатного и платного аккаунта. Логин на PythonAnywhere далее обозначен как
`yourusername` — везде замените на свой.

> Важно: проект сгенерирован на **Django 6.0**, которому нужен **Python 3.12+**.
> На PythonAnywhere выбирайте **Python 3.13**.

---

## Что уже подготовлено в проекте

- `requirements.txt` — зависимости (Django, Pillow, python-dotenv).
- `config/settings.py` читает секреты из переменных окружения:
  - `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` берутся из `.env` (или окружения).
  - При `DEBUG=False` автоматически включаются `SESSION_COOKIE_SECURE`,
    `CSRF_COOKIE_SECURE`, `SECURE_CONTENT_TYPE_NOSNIFF`, `SECURE_PROXY_SSL_HEADER`
    и заполняется `CSRF_TRUSTED_ORIGINS`.
- `.env.example` — шаблон переменных. `.env` уже в `.gitignore`, в репозиторий не попадёт.

---

## Шаг 1. Залить код на GitHub

Локально, из папки проекта:

```bash
git add .
git commit -m "Подготовка к деплою на PythonAnywhere"
git push origin main
```

Репозиторий уже настроен: `https://github.com/ZentifyID/django-fitness.git`.

---

## Шаг 2. Склонировать проект на PythonAnywhere

На сайте PythonAnywhere откройте вкладку **Consoles → Bash** и выполните:

```bash
cd ~
git clone https://github.com/ZentifyID/django-fitness.git
cd django-fitness
```

---

## Шаг 3. Создать виртуальное окружение и поставить зависимости

```bash
mkvirtualenv --python=/usr/bin/python3.13 fitness-venv
pip install -r requirements.txt
```

После этого окружение `fitness-venv` активно (видно `(fitness-venv)` в начале строки).
Запомните его путь — он понадобится на вкладке Web:
`/home/yourusername/.virtualenvs/fitness-venv`.

---

## Шаг 4. Создать файл `.env`

Сгенерируйте секретный ключ:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Создайте `.env` в корне проекта (`nano .env`) со своими значениями:

```env
SECRET_KEY=вставьте-сгенерированный-ключ
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
```

Сохраните: `Ctrl+O`, `Enter`, затем `Ctrl+X`.

---

## Шаг 5. Миграции, статика, суперпользователь

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

`collectstatic` соберёт всё в папку `static/` — её мы пропишем на вкладке Web.

---

## Шаг 6. Создать веб-приложение

1. Вкладка **Web → Add a new web app**.
2. На бесплатном аккаунте домен будет `yourusername.pythonanywhere.com` — нажмите Next.
3. Framework: выберите **Manual configuration** (НЕ «Django»).
4. Python version: **Python 3.13**. Next.

---

## Шаг 7. Указать виртуальное окружение

На вкладке **Web**, в секции **Virtualenv**, впишите:

```
/home/yourusername/.virtualenvs/fitness-venv
```

---

## Шаг 8. Настроить WSGI-файл

В секции **Code** нажмите на ссылку WSGI configuration file
(`/var/www/yourusername_pythonanywhere_com_wsgi.py`). Удалите всё содержимое и
вставьте:

```python
import os
import sys

path = '/home/yourusername/django-fitness'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

`.env` подхватится автоматически — `settings.py` вызывает `load_dotenv()`. Сохраните файл.

---

## Шаг 9. Прописать статику и медиа

На вкладке **Web**, в секции **Static files**, добавьте две строки:

| URL        | Directory                                  |
|------------|--------------------------------------------|
| `/static/` | `/home/yourusername/django-fitness/static` |
| `/media/`  | `/home/yourusername/django-fitness/media`  |

(На бесплатном аккаунте медиа-файлы, загруженные пользователями через админку,
тоже будут отдаваться отсюда.)

---

## Шаг 10. Перезапустить и проверить

Нажмите большую зелёную кнопку **Reload** вверху вкладки Web.
Откройте `https://yourusername.pythonanywhere.com` — сайт должен работать.
Админка: `https://yourusername.pythonanywhere.com/admin/`.

---

## Обновление сайта после изменений в коде

```bash
workon fitness-venv
cd ~/django-fitness
git pull origin main
pip install -r requirements.txt        # если менялись зависимости
python manage.py migrate               # если менялись модели
python manage.py collectstatic --noinput
```

Затем нажмите **Reload** на вкладке Web.

---

## Если что-то не работает

- **Error 500 / DisallowedHost** — проверьте, что в `.env` верный `ALLOWED_HOSTS`,
  и что вы нажали Reload.
- **Не грузятся стили/картинки** — проверьте пути в секции Static files и что
  `collectstatic` отработал без ошибок.
- **CSRF verification failed в админке** — убедитесь, что `DEBUG=False` и домен
  указан в `ALLOWED_HOSTS` (тогда `CSRF_TRUSTED_ORIGINS` соберётся автоматически).
- **Логи ошибок** — на вкладке Web, ссылки **Error log** и **Server log**.

---

## Заметка про базу данных

Сейчас используется SQLite (`db.sqlite3`) — для учебного/небольшого проекта этого
достаточно и на PythonAnywhere работает из коробки. Файл БД создастся при `migrate`.
Если в будущем понадобится MySQL — его можно подключить на вкладке **Databases**
и переопределить `DATABASES` через переменные окружения.
