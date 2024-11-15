from rest_framework.validators import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from reviews.models import Category, Comment, Review, Genre, Title


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
    rating = SerializerMethodField(
        read_only=True, default=None
    )

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
