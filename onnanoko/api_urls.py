from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import SeriesViewSet, GroupViewSet, TagViewSet, CharacterViewSet, ImageViewSet

router = DefaultRouter()
router.register(r'series', SeriesViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'tags', TagViewSet)
router.register(r'characters', CharacterViewSet)
router.register(r'images', ImageViewSet)

urlpatterns = router.urls
