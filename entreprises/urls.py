from django.urls import path
from entreprises.views import *

urlpatterns = [
    path('', index)
]