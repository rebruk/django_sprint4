from typing import Union
from django.db import models
from .querysets import PostQuerySet
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()

MAX_TITLE_LENGTH = 256
MAX_NAME_LENGTH = 256

image = models.ImageField('Изображение', upload_to='media', blank=True)

class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено"
    )

    class Meta:
        abstract = True

class Category(BaseModel):
    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name="Заголовок"
    )
    description = models.TextField(verbose_name="Описание", blank=True)
    slug = models.SlugField(
        verbose_name="Идентификатор",
        unique=True,
        help_text="Идентификатор страницы для URL; "
                  "разрешены символы латиницы, цифры, дефис и подчёркивание."
    )

    class Meta(BaseModel.Meta):
        verbose_name = "категория"
        verbose_name_plural = "Категории"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name="Название места"
    )

    class Meta(BaseModel.Meta):
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name="Заголовок"
    )
    text = models.TextField( verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text="Если установить дату и время в будущем — "
                  "можно делать отложенные публикации.",
        default=timezone.now
    )
    image = models.ImageField(
        'Изображение',
        upload_to='post_images/',
        blank=True
    )
    content = models.TextField(null=True, blank=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name='posts'
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
        related_name='posts'
    )
    is_published = models.BooleanField(
        'Опубликовано',
        default=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    objects: Union[PostQuerySet, models.QuerySet] = PostQuerySet.as_manager()


    class Meta(BaseModel.Meta):
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self) -> str:
        return self.text