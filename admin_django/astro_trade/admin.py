from django.contrib import admin
from .models import (
    Data, Info, Payments, Users
)


@admin.register(Data)
class DataAdmin(admin.ModelAdmin):
    list_display = ('date', 'text')
    fields = ('date', 'text')
    list_editable = ('text', )


@admin.register(Info)
class DataAdmin(admin.ModelAdmin):
    list_display = ('page_name', 'page_text')
    fields = ('page_name', 'page_text')
    list_editable = ('page_text', )


@admin.register(Payments)
class DataAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'payment_code', 'payment_status', 'value', 'href')
    fields = ('user_id', 'payment_code', 'payment_status', 'value', 'href')


@admin.register(Users)
class DataAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'first_name', 'last_name', 'role', 'balance', 'expired')
    fields = ('user_id', 'username', 'first_name', 'last_name', 'role', 'balance', 'expired')
    list_editable = ('username', 'first_name', 'last_name', 'role', 'balance', 'expired')
