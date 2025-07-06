from rest_framework.response import Response
from rest_framework import status
from users.models import UserProfile
from .models import Prediction
from functools import wraps
from datetime import datetime

def enforce_quota(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        if profile.is_pro:
            return view_func(self, request, *args, **kwargs)
        today = datetime.utcnow().date()
        count = Prediction.objects.filter(user=request.user, requested_at__date=today).count()
        if count >= profile.daily_quota:
            return Response({"error": "Daily quota exceeded. Upgrade to Pro."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        return view_func(self, request, *args, **kwargs)
    return _wrapped_view