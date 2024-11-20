from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet
)

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('users', UserViewSet, basename='users')
v1_router.register('titles', TitleViewSet, basename='title')
v1_router.register('genres', GenreViewSet, basename='genre')
v1_router.register('categories', CategoryViewSet, basename='category')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)

auth_urlpatterns = [
    path('signup/',
         UserViewSet.as_view({'post': 'signup'}),
         name='signup'),
    path('token/',
         UserViewSet.as_view({'post': 'token'}),
         name='token_obtain_pair'),
]

v1_urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include(auth_urlpatterns)),
]

urlpatterns = [
    path('v1/', include(v1_urlpatterns)),
]
