from django.urls import path
from .views import index_page, new_match

urlpatterns = [
    path('list', index_page, name='matches_list'),
    path('new', new_match, name='matches_new')
]