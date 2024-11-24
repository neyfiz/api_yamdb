from django.contrib.auth.tokens import default_token_generator
from django.core.validators import RegexValidator, EmailValidator
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import IntegerField, ModelSerializer
from rest_framework.validators import ValidationError

from reviews.constants import (
    MAX_LENGTH_ROLE,
    MAX_REVIEW,
    MIN_REVIEW,
    MAX_LENGTH_EMAIL,
    NOT_ALLOWED_USERNAMES,
    USERNAME_SEARCH_REGEX,
    VALIDATE_DATE_ERROR
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

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            username=validated_data.get('username'),
            defaults=validated_data
        )
        return user

    def validate_role(self, value):
        if value not in UserRole.values:
            raise serializers.ValidationError('Недопустимая роль.')
        return value

    def validate_username(self, value):
        if value in NOT_ALLOWED_USERNAMES:
            raise ValidationError("Этот никнейм нельзя использовать")

        if self.instance is None:
            if User.objects.filter(username=value).exists():
                raise ValidationError("Имя пользователя уже существует")
        return value

    def validate_email(self, value):
        if self.instance is None:
            if User.objects.filter(email=value).exists():
                raise ValidationError(
                    "Пользователь с данным email уже существует")
        return value

    def update(self, instance, validated_data):
        validated_data.pop('role', None)
        return super().update(instance, validated_data)


class UserSignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=MAX_LENGTH_ROLE,
        validators=[
            RegexValidator(
                regex=USERNAME_SEARCH_REGEX,
                message='Имя пользователя может содержать только буквы, '
                        'цифры и символы: @/./+/-/_'
            )
        ]
    )
    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        validators=[EmailValidator(message='Некорректный email-адрес.')]
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value in NOT_ALLOWED_USERNAMES:
            raise serializers.ValidationError(
                f"Имя пользователя '{value}' недопустимо."
            )
        return value

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')

        user = User.objects.filter(username=username).first()

        if user:
            if user.email != email:
                raise serializers.ValidationError(
                    {'email': 'Email не совпадает с уже зарегистрированным'
                              'пользователем.'}
                )
        elif User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Пользователь с данным email уже существует.'}
            )

        return attrs

    def create(self, validated_data):
        user, _ = User.objects.get_or_create(
            username=validated_data['username'],
            defaults={'email': validated_data['email']}
        )
        return user


class TokenObtainSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, attrs):
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'})

        attrs['user'] = user
        return attrs


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
    rating = IntegerField(read_only=True)

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
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
        required=True
    )
    year = IntegerField()

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        year = timezone.datetime.now().year
        if value > year:
            raise ValidationError(
                VALIDATE_DATE_ERROR.format(year=year)
            )
        return value

    def to_representation(self, value):
        return TitleReadSerializer(value).data


class ReviewSerializer(ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

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
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
