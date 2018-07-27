from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()
router.register(r'characters', views.CharactersViewset)
router.register(r'matches', views.MatchesViewset)

urlpatterns = [
    path('', include(router.urls))
]