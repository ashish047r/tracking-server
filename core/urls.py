from django.urls import path
from .views import get_suffix, run_single

urlpatterns = [
    path("script/suffix/", get_suffix),
    path("run/", run_single),
]
