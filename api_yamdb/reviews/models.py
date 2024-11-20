from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import (
    MAX_LENGTH,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_ROLE,
)


# Роли пользователей
class UserRole(models.TextChoices):
    USER = 'user', 'User'
    MODERATOR = 'moderator', 'Moderator'
    ADMIN = 'admin', 'Admin'


# Пользователь
class User(AbstractUser):
    email = models.EmailField(max_length=MAX_LENGTH_EMAIL, unique=True)
    role = models.CharField(
        max_length=MAX_LENGTH_ROLE,
        choices=UserRole.choices,
        default=UserRole.USER
    )
    bio = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True,
        help_text=(
            'Группы, к которым принадлежит пользователь. '
            'Пользователь получит все разрешения каждой из групп.'
        ),
        verbose_name='Группы',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True,
        help_text='Специальные разрешения для данного пользователя.',
        verbose_name='Права пользователя',
    )

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.username


class SlugCategoryGenreModel(models.Model):
    name = models.CharField('Имя', max_length=MAX_LENGTH)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(SlugCategoryGenreModel):
    name = models.CharField('Имя категории', max_length=MAX_LENGTH)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(SlugCategoryGenreModel):
    name = models.CharField('Имя жанра', max_length=MAX_LENGTH)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField('Название произведения', max_length=MAX_LENGTH)
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        through='GenreTitle',
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=True,
        verbose_name='Категория',
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание'
    )
    year = models.SmallIntegerField(
        db_index=True,
        verbose_name='Год выпуска'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name', 'year')

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение',
        related_name='genretitle',
    )
    genre = models.ForeignKey(
        Genre,
        related_name='genretitle',
        on_delete=models.SET_NULL,
        verbose_name='Жанр',
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.genre.name} {self.title.name}'


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField('Оценка', blank=True, null=True)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        unique_together = ('title', 'author')

    def __str__(self):
        return f'Review by {self.author} on {self.title}'


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f"Комментарий от {self.author.username} к отзыву на {self.review.title.name}"
