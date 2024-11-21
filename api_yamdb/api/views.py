from http import HTTPStatus

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin
)
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated
)
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, User

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
    UserSerializer,
    TokenObtainSerializer, UserSignupSerializer
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

    def get_permissions(self):
        print(f'Action: {self.action}')

        if self.action in ['signup', 'token']:
            return [AllowAny()]

        elif self.action in ['list', 'retrieve',
                             'destroy', 'partial_update']:
            return [IsAdminOrAuthenticated()]
        return super().get_permissions()

    def retrieve(self, request, *args, **kwargs):
        username = kwargs.get('pk')
        user = get_object_or_404(User, username=username)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        username = kwargs.get('pk')
        user = get_object_or_404(User, username=username)
        user.delete()
        return Response(status=HTTPStatus.NO_CONTENT)

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

                print(f'Код для уже созданного пользователя '
                      f'{confirmation_code}')

                return Response(
                    {'username': existing_user.username,
                     'email': existing_user.email},
                    status=HTTPStatus.OK
                )

            return Response(
                {'email':
                 'Email не совпадает с уже зарегистрированным пользователем.'},
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

            print(f'Сохранённый код для нового пользователя: {username} - '
                  f'{confirmation_code}')

            return Response(response_data, status=HTTPStatus.OK)

        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='me')
    def me(self, request):
        user = request.user

        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data,
                                             partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=HTTPStatus.OK)

        serializer = self.get_serializer(user)
        return Response(serializer.data)


class SignupAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')

        user = User.objects.filter(username=username).first()

        if user:
            if user.email == email:
                return Response(
                    {'username': user.username, 'email': user.email},
                    status=HTTPStatus.OK
                )
            return Response(
                {'email': 'Email не совпадает с уже зарегистрированным пользователем.'},
                status=HTTPStatus.BAD_REQUEST
            )

        serializer = UserSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=RESPONSE_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {'username': user.username, 'email': user.email},
            status=HTTPStatus.OK
        )

class TokenObtainAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenObtainSerializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except NotFound as e:
            return Response(e.args[0], status=HTTPStatus.NOT_FOUND)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'token': str(refresh.access_token),
        }, status=HTTPStatus.OK)


class CreateListDestroyViewSet(CreateModelMixin, DestroyModelMixin,
                               ListModelMixin, GenericViewSet):
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
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('name')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitlePostSerializer

    def to_representation(self, value):
        return TitleReadSerializer(value).data


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
