from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("nouvel_elevage", views.nouvel_elevage, name="nouvel_elevage"),
    path("voir_elevage/<int:pk>", views.voir_elevage, name="voir_elevage"),
]