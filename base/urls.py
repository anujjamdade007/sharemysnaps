from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index , name="home"),

    # authentication
    path('login/', views.login, name='login'),
    # path('signup/', views.user_signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('social_auth/', include('social_django.urls' , namespace='social')),

]