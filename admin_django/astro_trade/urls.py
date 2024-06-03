from django.urls import path
from . import views

app_name = 'astro_trade'

urlpatterns = [
    path('', views.index, name='astro_trade'),
]
