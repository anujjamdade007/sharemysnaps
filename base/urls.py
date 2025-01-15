from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', views.index , name="home"),

    # authentication
    path('login/', views.login, name='login'),
    # path('signup/', views.user_signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('social_auth/', include('social_django.urls' , namespace='social')),

    path('privacy-policy/', views.privacy, name='privacy'),

    path('terms-condition/', views.terms, name='terms'),

    path('favicon.ico', RedirectView.as_view(url='/staticfiles/favicon.ico'))

]