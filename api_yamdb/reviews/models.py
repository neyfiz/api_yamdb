from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.exceptions import ValidationError

from .constants import (
    MAX_LENGTH,
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_ROLE,
    MAX_LENGTH_SLUG,
    NOT_ALLOWED_USERNAMES
)

ROLE_USER = 'user'
ROLE_MODERATOR = 'moderator'
ROLE_ADMIN = 'admin'


class UserRole(models.TextChoices):
    USER = ROLE_USER, 'Пользователь'
    MODERATOR = ROLE_MODERATOR, 'Модератор'
    ADMIN = ROLE_ADMIN, 'Администратор'


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

    @property
    def is_admin(self):
        """Проверяет, является ли пользователь администратором."""
        return (
            self.is_superuser
            or self.is_staff
            or self.role == UserRole.ADMIN)

    @property
    def is_moderator(self):
        """Проверяет, является ли пользователь модератором."""
        return self.role == UserRole.MODERATOR

    class Meta:
        verbose_name = 'Юзер'
        verbose_name_plural = 'Юзеры'
        ordering = ('role',)

    def clean(self):
        super().clean()
        if self.username in NOT_ALLOWED_USERNAMES:
            raise ValidationError(
                f'Имя пользователя не может быть {NOT_ALLOWED_USERNAMES}.')

    def __str__(self):
        return self.username


class Category(models.Model):
    name = models.CharField('Имя категории', max_length=MAX_LENGTH)
    slug = models.SlugField('Слаг', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Имя жанра', max_length=MAX_LENGTH)
    slug = models.SlugField('Слаг', max_length=MAX_LENGTH_SLUG, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


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


<<<<<<< HEAD
class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField(verbose_name="Оценка", blank=True, null=True)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        unique_together = ('title', 'author')
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'Review by {self.author} on {self.title}'


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
=======
class ReviewCommentBase(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
>>>>>>> develop
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        abstract = True
        ordering = ['text']
        verbose_name = 'Комментарий/Отзыв'
        verbose_name_plural = 'Комментарии/Отзывы'


class Review(ReviewCommentBase):
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    score = models.IntegerField(verbose_name="Оценка", blank=True, null=True)

    class Meta:
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_title_author'
            )
        ]

    def __str__(self):
        return f'Отзыв от {self.author} на {self.title}'


class Comment(ReviewCommentBase):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)

    class Meta:
        default_related_name = 'comments'
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return (
            f"Комментарий от {self.author.username} к отзыву на "
            f"{self.review.title.name}"
        )
