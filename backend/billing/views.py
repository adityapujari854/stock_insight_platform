from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from users.models import UserProfile
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class SubscribeView(APIView):
    """
    Creates a Stripe Checkout Session for Pro Subscription (test mode only).
    NOTE: Stripe India test keys used, no real payments will be processed.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = UserProfile.objects.get(user=user)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email=user.email,
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {'name': 'Pro Subscription'},
                    'unit_amount': 19900,
                    'recurring': {'interval': 'month'},
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',
            metadata={'user_id': user.id}
        )
        return Response({'checkout_url': session.url})

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Handles Stripe webhook events (test mode only).
    NOTE: Stripe India test keys used, no real payments will be processed.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        event = None
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata'].get('user_id')
            try:
                profile = UserProfile.objects.get(user_id=user_id)
                profile.is_pro = True
                profile.save()
            except UserProfile.DoesNotExist:
                pass
        return Response({'status': 'success'})