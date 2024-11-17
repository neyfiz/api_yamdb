import random
from http import HTTPStatus

from rest_framework.exceptions import MethodNotAllowed
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
)
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


from reviews.models import (User, Category,
                            Genre, Review, Title)
from .permissions import IsAdmin

from .permissions import IsAuthorOrReadOnly, IsAdminOrModerator
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
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    permission_classes = [IsAuthenticated]

    # Определяем доступы
    def get_permissions(self):
        print(f'Action: {self.action}')

        if self.action in ['signup', 'token']:
            return [AllowAny()]

        elif self.action in ['list', 'retrieve',
                             'destroy', 'update',
                             'partial_update']:
            return [IsAdmin()]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        username = kwargs.get('pk')
        user = get_object_or_404(User, username=username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='auth/signup')
    def signup(self, request):

        username = request.data.get('username')
        email = request.data.get('email')

        if username == 'me':
            return Response(
                {'username': 'Этот никнейм нельзя использовать'},
                status=HTTPStatus.BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            existing_user = User.objects.get(username=username)

            if existing_user.email != email:
                return Response(
                    {'email': 'Email не совпадает с уже зарегистрированным пользователем.'},
                    status=HTTPStatus.BAD_REQUEST
                )
            return Response(
                {'username': existing_user.username,
                 'email': existing_user.email},
                status=HTTPStatus.OK
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response_data = {
                'username': user.username,
                'email': user.email
            }

            confirmation_code = random.randint(100000, 999999)

            send_mail(
                subject='Код подтверждения',
                message=f'Ваш код подтверждения: {confirmation_code}',
                from_email='noreply@yamdb.fake',
                recipient_list=[user.email],
                fail_silently=False,
            )
            request.session['confirmation_code'] = confirmation_code
            print(f'Сохранённый код: {confirmation_code}')

            return Response(response_data, status=HTTPStatus.OK)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(user, data=request.data,
                                             partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=HTTPStatus.OK)
            return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='auth/token')
    def token(self, request):
        username = request.data.get('username')
        confirmation_code = request.data.get('confirmation_code')

        if not username:
            return Response({'detail': 'Укажите никнейм.'},
                            status=HTTPStatus.BAD_REQUEST)
        if not confirmation_code:
            return Response({'detail': 'Укажите код подтверждения.'},
                            status=HTTPStatus.BAD_REQUEST)

        user = get_object_or_404(User, username=username)

        stored_code = request.session.get('confirmation_code')
        print(f'Извлеченный код из сессии: {stored_code}')

        # тут уязвимость, AllowAny in signup, token код выдаеться из последней сессии,
        # можно создать админа от юзера с этим же кодом, в теории

        if not stored_code:
            return Response({'detail': 'Код подтверждения не найден, укажите его заново.'},
                            status=HTTPStatus.BAD_REQUEST)

        if str(confirmation_code) != str(stored_code):
            return Response({'detail': 'Неверный код подтверждения.'},
                            status=HTTPStatus.BAD_REQUEST)


        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'token': str(refresh.access_token),
            },
        status=HTTPStatus.OK
        )


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
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

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
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Review, id=review_id, title__id=title_id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()
