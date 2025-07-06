from django.urls import path
from .views import SubscribeView, StripeWebhookView

urlpatterns = [
    path('subscribe/', SubscribeView.as_view(), name='subscribe'),
    path('webhooks/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
]