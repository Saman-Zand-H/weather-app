from django.urls import path

from . import views

app_name = "wth"
urlpatterns = [
    path('', views.homeview, name='home'),
    path('contact/', views.contactview, name='contact'),
    path('choose-unit/', views.unitview, name='unit'),
    path('set-city/', views.defaultcityview, name='set-city'),
    path('remove-city/', views.removecityview, name='remove-city'),
]
