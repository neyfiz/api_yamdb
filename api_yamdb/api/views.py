from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework.mixins import (CreateModelMixin,
                                   DestroyModelMixin, ListModelMixin)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework import views

from .serializers import (
    CategorySerializer, CommentSerializer,
    GenreSerializer, ReviewSerializer,
    TitleReadSerializer, TitlePostSerializer
)
from reviews.models import Category, Genre, Review, Title


# допишу классы
class SignUpView(views.APIView):
    pass


class TokenView(views.APIView):
    pass


class UserProfileView(views.APIView):
    pass


class CreateListDestroyViewSet(CreateModelMixin, DestroyModelMixin,
                               ListModelMixin, GenericViewSet):
    pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitlePostSerializer


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all()


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Review, id=review_id, title__id=title_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()
