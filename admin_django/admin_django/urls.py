from django.contrib import admin
from django.urls import include, path
from astro_trade import views


urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('astro_trade.urls', namespace='index')),
]