from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet, ReviewViewSet

v1_router = DefaultRouter()


v1_router.register('reviews', ReviewViewSet, basename='reviews')
v1_router.register(
    r'reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='review-comments'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
