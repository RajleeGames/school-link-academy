from django.urls import path
from . import views

urlpatterns = [
    path("switch-language/", views.switch_language, name="switch_language"),
]