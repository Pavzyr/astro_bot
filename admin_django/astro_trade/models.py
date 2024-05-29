from django.db import models


class Data(models.Model):
    date = models.TextField(blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data'
        verbose_name = "Прогноз по датам"
        verbose_name_plural = "Прогнозы по датам"


class Info(models.Model):
    page_name = models.TextField(blank=True, null=True)
    page_text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'info'
        verbose_name = "Текстовки информации"
        verbose_name_plural = "Текстовки информации"


class Payments(models.Model):
    user_id = models.TextField(blank=True, null=True)
    payment_code = models.TextField(blank=True, null=True)
    payment_status = models.TextField(blank=True, null=True)
    value = models.TextField(blank=True, null=True)
    href = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payments'
        verbose_name = "Оплаты"
        verbose_name_plural = "Оплаты"


class Users(models.Model):
    user_id = models.IntegerField(unique=True, blank=True, null=True)
    username = models.TextField(blank=True, null=True)
    first_name = models.TextField(blank=True, null=True)
    last_name = models.TextField(blank=True, null=True)
    role = models.TextField(blank=True, null=True)
    balance = models.TextField(blank=True, null=True)
    expired = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
        verbose_name = "Пользователи"
        verbose_name_plural = "Пользователи"
