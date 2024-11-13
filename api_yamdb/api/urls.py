from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet, ReviewViewSet,
    TitleViewSet, SignUpView, TokenView, UserProfileView
)

app_name = 'api'

v1_router = DefaultRouter()


v1_router.register('titles', TitleViewSet, basename='title')
v1_router.register('genres', GenreViewSet, basename='category')
v1_router.register('categories', CategoryViewSet, basename='category')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comment'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)

v1_urlpatterns = [
    path('', include(v1_router.urls)),
]

urlpatterns = [
    path('v1/', include(v1_urlpatterns)),

    # Эндпоинты для авторизации и получения токена
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token_obtain'),
    path('users/me/', UserProfileView.as_view(), name='user_profile'),
]
