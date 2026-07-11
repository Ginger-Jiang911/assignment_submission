from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("submit/<slug:slug>/", views.submit_project_view, name="submit_project"),
]