from django.urls import path
from .views import get_suffix

urlpatterns = [
    path("script/suffix/", get_suffix),
]
