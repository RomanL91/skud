from django.contrib import admin

from app_telegram.models import TelegramPusher


@admin.register(TelegramPusher)
class TelegramPusherAdmin(admin.ModelAdmin):
    readonly_fields = ['status',]
