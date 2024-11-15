from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UserViewSet, CategoryViewSet, CommentViewSet,
    GenreViewSet, ReviewViewSet, TitleViewSet
)

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('users', UserViewSet, basename='users')
v1_router.register('titles', TitleViewSet, basename='title')
v1_router.register('genres', GenreViewSet, basename='genre')
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
    path('v1/auth/signup/', UserViewSet.as_view({'post': 'signup'}), name='signup'),
    path('v1/auth/token/', UserViewSet.as_view({'post': 'token'}), name='token_obtain_pair'),
]
