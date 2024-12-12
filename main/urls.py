from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard , name="dashboard"),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('sync-folder/', views.sync_folders, name='sync_folder'),

]