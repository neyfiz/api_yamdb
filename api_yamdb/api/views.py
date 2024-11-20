import random
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from http import HTTPStatus
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .filters import TitleFilter
from .permissions import (
    IsAdminModeratorAuthorOrReadOnly,
    IsAdminOnly,
    IsAdminOrAuthenticated
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitlePostSerializer,
    TitleReadSerializer,
    UserSerializer
)
from reviews.models import (
    Category,
    Genre,
    Review,
    Title,
    User
)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    # Определяем доступы
    def get_permissions(self):
        if self.action in ['signup', 'token']:
            return [AllowAny()]

        elif self.action in ['list', 'retrieve',
                             'destroy', 'partial_update']:
            return [IsAdminOrAuthenticated()]
        return super().get_permissions()

    # GET получить один обьект по pk
    def retrieve(self, request, *args, **kwargs):
        username = kwargs.get('pk')
        user = get_object_or_404(User, username=username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    # PUT
    def update(self, request, *args, **kwargs):
        return Response({'detail: Метод PUT не разрешён.'}, status=HTTPStatus.METHOD_NOT_ALLOWED)

    # DELETE
    def destroy(self, request, *args, **kwargs):
        username = kwargs.get('pk')
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

    # PATCH
    def partial_update(self, request, *args, **kwargs):
        username = kwargs.get('pk')
        user = get_object_or_404(User, username=username)

        data = request.data.copy()

        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.OK)

    @action(detail=False, methods=['post'], url_path='auth/signup')
    def signup(self, request):

        username = request.data.get('username')
        email = request.data.get('email')

        print(f'{username}')

        if username == 'me':
            return Response(
                {'username': 'Этот никнейм нельзя использовать'},
                status=HTTPStatus.BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            existing_user = User.objects.get(username=username)

            if existing_user.email == email:
                confirmation_code = random.randint(100000, 999999)
                request.session['confirmation_code'] = confirmation_code

                print(f'Код для уже созданого пользователя {confirmation_code}')

                return Response(
                    {'username': existing_user.username, 'email': existing_user.email},
                    status=HTTPStatus.OK
                )

            return Response(
                {'email': 'Email не совпадает с уже зарегистрированным пользователем.'},
                status=HTTPStatus.BAD_REQUEST
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

            print(f'Сохранённый код для нового пользователя: {username} - {confirmation_code}')

            return Response(response_data, status=HTTPStatus.OK)

        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method in ['PUT', 'PATCH']:
            if 'role' in request.data:
                return Response({'detail': 'Невозможно изменить роль с ключом role'})

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
    permission_classes = (IsAdminOnly,)
    lookup_field = 'slug'
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    pagination_class = PageNumberPagination


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    permission_classes = (IsAdminOnly,)
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitlePostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Title, id=title_id)

    def perform_create(self, serializer):
        title = self.get_title()
        serializer.save(author=self.request.user, title=title)

    def get_queryset(self):
        title = self.get_title()
        return title.reviews.all().order_by('pub_date')


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModeratorAuthorOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        review_id = self.kwargs.get('review_id')
        title_id = self.kwargs.get('title_id')
        return get_object_or_404(Review, id=review_id, title__id=title_id)

    def perform_create(self, serializer):
        review = self.get_review()
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = self.get_review()
        return review.comments.all()
