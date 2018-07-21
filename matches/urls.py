from django.urls import path
from .views import index_page, new_match, edit_match, delete_match

urlpatterns = [
    path('list', index_page, name='matches_list'),
    path('new', new_match, name='matches_new'),
    path('edit/<int:pk>', edit_match, name='matches_edit'),
    path('delete/<int:pk>', delete_match, name='matches_delete')
]