from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from .querysets import PostQuerySet, CategoryQuerySet

User = get_user_model()

MAX_TITLE_LENGTH = 256
MAX_NAME_LENGTH = 20


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        blank=False,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        verbose_name="Добавлено"
    )

    class Meta:
        abstract = True


class BaseModelComments(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=False,
        verbose_name="Добавлено"
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name="Заголовок"
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=False
    )
    slug = models.SlugField(
        verbose_name="Идентификатор",
        unique=True,
        blank=False,
        help_text="Идентификатор страницы для URL; "
                  "разрешены символы латиницы, цифры, дефис и подчёркивание."
    )

    objects = CategoryQuerySet.as_manager()

    class Meta(BaseModel.Meta):
        verbose_name = "категория"
        verbose_name_plural = "Категории"
        ordering = ['title']

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        blank=False,
        verbose_name="местоположение"
    )

    class Meta(BaseModel.Meta):
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(BaseModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
        verbose_name="Автор публикации",
    )
    location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
    )

    title = models.CharField(
        max_length=MAX_TITLE_LENGTH,
        verbose_name="Заголовок"
    )
    text = models.TextField(blank=False, verbose_name='Текст')
    pub_date = models.DateTimeField(
        blank=False,
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

    objects = PostQuerySet.as_manager()

    class Meta(BaseModel.Meta):
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        default_related_name = 'posts'

    def __str__(self):
        return self.title


class Comment(BaseModelComments):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    text = models.TextField('Текст комментария')
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
        default_related_name = 'comments'  # Выносим related_name по умолчанию

    def __str__(self) -> str:
        return self.text
