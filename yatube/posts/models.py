from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models. CharField(
        max_length=200,
        verbose_name='Название группы',
        help_text='Введите название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Адрес группы',
        help_text='Введите адрес'
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text='Введите описание'
    )

    class Meta:
        verbose_name = 'Создать новую группу'
        verbose_name_plural = 'Создать новую группу'

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст',
        help_text='О чём Вы сейчас думаете?'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
        help_text='Укажите автора'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберете группу, к которой относится Ваша заметка'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self) -> str:
        return self.text

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Создать новую заметку'
        verbose_name_plural = 'Создать новую заметку'


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Комментарий',
        )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост',
        related_name='comments',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )
