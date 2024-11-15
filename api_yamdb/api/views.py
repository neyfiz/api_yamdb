from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework.mixins import (CreateModelMixin,
                                   DestroyModelMixin, ListModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from reviews.models import (User, Category,
                            Genre, Review, Title)

from .serializers import (
    UserSerializer, CategorySerializer,
    CommentSerializer,
    GenreSerializer, ReviewSerializer,
    TitleReadSerializer, TitlePostSerializer
)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination

    # Определяем доступы
    def get_permissions(self):
        if self.action in ['signup', 'token']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        username = kwargs.get('pk')
        user = get_object_or_404(User, username=username)
        if not user:
            return Response({'detail': 'Пользователь не найден.'}, status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='auth/signup')
    def signup(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        user = request.user
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=HTTP_200_OK)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='auth/token')
    def token(self, request):
        serializer = TokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


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
