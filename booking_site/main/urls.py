from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name = 'home'),
    path('events', views.events, name = 'events'),
    path('events/<int:event_id>/register/', views.register_event, name='register_event'),
    path('contacts', views.contacts, name = 'contacts'),

    path('register', views.registerPage, name = 'register'),
    path('login', views.loginPage, name = 'login'),
    path('logout', views.logoutUser, name='logout'),
    path('profile', views.profile, name = 'profile'),
    path('become-organizer/', views.become_organizer, name='become_organizer'),
    path('create-event/', views.create_event, name='create_event'),
    path('moderation/', views.moderation_panel, name='moderation_panel'),
    path('moderation/approve/<int:event_id>/', views.approve_event, name='approve_event'),
    path('moderation/reject/<int:event_id>/', views.reject_event, name='reject_event'),

]