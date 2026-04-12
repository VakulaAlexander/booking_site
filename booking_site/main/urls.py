from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name = 'home'),
    path('events', views.events, name = 'events'),
    path('contacts', views.contacts, name = 'contacts'),

    path('register', views.registerPage, name = 'register'),
    path('login', views.loginPage, name = 'login'),
    path('logout', views.logoutUser, name='logout'),
    path('profile', views.profile, name = 'profile'),
]