from django.contrib import admin

from app_telegram.models import TelegramPusher


@admin.register(TelegramPusher)
class TelegramPusherAdmin(admin.ModelAdmin):
    readonly_fields = ['phone_number_status', 'secret_pass_status', 'status',]
