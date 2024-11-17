from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from reviews.models import (User, Category,
                            Comment, Review,
                            Genre, Title)


class UserSerializer(ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message=
                'Имя пользователя может содержать только буквы,'
                ' цифры и символы: @/./+/-/_'
            )
        ]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'first_name', 'last_name', 'bio']

    def validate_username(self, value):
        if value.lower() == 'me':
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


class TitleReadSerializer(ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer(many=False)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category',
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

    def to_representation(self, value):
        return TitleReadSerializer(value).data


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
        return data


class CommentSerializer(ModelSerializer):
    author = SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
