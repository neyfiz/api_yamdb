from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import ValidationError

from reviews.constants import (
    MAX_LENGTH_ROLE,
    MAX_REVIEW,
    MIN_REVIEW,
    NOT_ALLOWED_USERNAMES,
    USERNAME_SEARCH_REGEX
)
from reviews.models import (
    Category,
    Comment,
    Genre,
    Review,
    Title,
    User,
    UserRole
)


class UserSerializer(ModelSerializer):
    username = serializers.CharField(
        max_length=MAX_LENGTH_ROLE,
        validators=[
            RegexValidator(
                regex=USERNAME_SEARCH_REGEX,
                message='Имя пользователя может содержать только буквы,'
                        ' цифры и символы: @/./+/-/_'
            )
        ]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'first_name', 'last_name', 'bio'
        )

    def validate_role(self, value):
        if value not in UserRole.values:
            raise serializers.ValidationError('Недопустимая роль.')
        return value

    def validate_username(self, value):
        if value in NOT_ALLOWED_USERNAMES:
            raise ValidationError("Этот никнейм нельзя использовать")
        if User.objects.filter(username=value).exists():
            raise ValidationError("Имя пользователя уже существует")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError("Пользователь с данным email уже существует")
        return value


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer(many=False)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitlePostSerializer(ModelSerializer):
    category = SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )
    genre = SlugRelatedField(
        many=True, queryset=Genre.objects.all(), slug_field='slug'
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        if request.method == 'POST':
            if Review.objects.filter(title=title_id, author=author).exists():
                raise ValidationError(
                    'Можно создать только 1 отзыв на 1 произведение'
                )
            score = data.get('score')
            if score is not None and not (MIN_REVIEW <= score <= MAX_REVIEW):
                raise ValidationError(
                    f'Оценка должна быть от {MIN_REVIEW} до {MAX_REVIEW}.')
        return data


class CommentSerializer(ModelSerializer):
    author = SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
