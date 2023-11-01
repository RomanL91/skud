from django.contrib import admin

from app_telegram.models import TelegramPusher


@admin.register(TelegramPusher)
class TelegramPusherAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'phone_number_status', 'secret_pass_status', 'status']
    readonly_fields = ['chat_id', 'phone_number_status', 'secret_pass_status',]
    search_fields = ['last_name__istartswith', ]
