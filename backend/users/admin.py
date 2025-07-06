from django.contrib import admin
from .models import UserProfile, TelegramUser

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_pro', 'daily_quota', 'stripe_customer_id')
    search_fields = ('user__username', 'stripe_customer_id')

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'chat_id', 'last_command', 'last_used')