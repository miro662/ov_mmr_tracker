from django.urls import path
from .views import index_page

urlpatterns = [
    path('list', index_page, name='matches_list')
]