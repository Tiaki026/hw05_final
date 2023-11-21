# Социальная сеть YaTube
## :page_with_curl: Описание
YaTube - это веб-приложение для обмена постами, где пользователи могут организовывать их по группам, загружать изображения, подписываться на авторов и комментировать посты.

### Основные функции
Создание постов: Пользователи могут создавать посты, добавлять текст и изображения.
Сортировка по группам: Посты можно отнести к определенным группам (темам), что облегчает их поиск и просмотр.
Загрузка изображений: Возможность прикреплять изображения к постам для визуального контента.
Подписка на авторов: Пользователи могут подписываться на других авторов и получать уведомления о их новых постах.
Комментирование постов: Возможность оставлять комментарии к постам других пользователей.

## :computer: Стек технологий
- ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

  Python: Язык программирования
- ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

  Django: Фреймворк для создания веб-приложений
- ![HTML](https://img.shields.io/badge/html5%20-%23E34F26.svg?&style=for-the-badge&logo=html5&logoColor=white)

  HTML: Язык гипертекстовой разметки документов для просмотра веб-страниц

## :page_with_curl: Как воспользоваться проектом
### Клонирование проекта с GitHub на компьютер
`git@github.com:Tiaki026/hw05_final.git`

### Настройка бэкенд-приложения
1.	Перейдите в директорию бэкенд-приложения проекта.
```
cd hw05_final/yatube/
```
2.	Создайте виртуальное окружение.

Linux
```
python3 -m venv venv
```
Windows
```
python -m venv venv
```
3.	Активируйте виртуальное окружение.

Linux
```
source venv/bin/activate
```
Windows
```
source venv/Scripts/activate
```
4.	Установите зависимости.
```
pip install -r requirements.txt
```
5.	Примените миграции.

Linux
```
python3 manage.py migrate
```
Windows
```
python manage.py migrate
```
6. Создайте админа.

Linux
```
python3 manage.py createsuperuser
```
Windows
```
python manage.py createsuperuser
```
7. Запустите сервер
Linux
```
python3 manage.py runserver
```
Windows
```
python manage.py runserver
```

## Автор:
  - [Колотиков Евгений](https://github.com/Tiaki026)
