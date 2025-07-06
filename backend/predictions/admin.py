from django.contrib import admin
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticker', 'predicted_price', 'requested_at')
    search_fields = ('ticker', 'user__username')