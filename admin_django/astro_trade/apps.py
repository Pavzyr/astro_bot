from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "astro_trade"
    verbose_name = 'Астро трейд бот'
