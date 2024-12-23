from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard , name="dashboard"),
    path('create-folder/', views.create_folder, name='create_folder'),
    path('sync-folder/', views.sync_folders, name='sync_folder'),
    # path('upload/<str:folder_id>/', views.upload_image_to_folder, name='upload_image_to_folder'),
    path('redirect_to_folder/<str:folder_id>/', views.redirect_to_folder, name='redirect_to_folder'),
    path('gallery/<str:folder_id>/', views.image_gallery, name='gallery'),
    path('serve_image/<str:image_ids>/', views.serve_image, name='serve_image'),
    path('customise/<str:folder_id>/', views.customize, name='customize'),
]