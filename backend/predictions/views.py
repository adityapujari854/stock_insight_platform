from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import Prediction
from .serializers import PredictionSerializer
from .utils import run_prediction
from .quota import enforce_quota
import os
from rest_framework.generics import ListAPIView

class PredictView(APIView):
    permission_classes = [IsAuthenticated]

    @enforce_quota
    def post(self, request):
        ticker = request.data.get('ticker')
        if not ticker:
            return Response({"error": "ticker is required"}, status=400)

        save_dir = os.path.join(settings.MEDIA_ROOT, 'predictions')
        os.makedirs(save_dir, exist_ok=True)

        try:
            result = run_prediction(
                ticker=ticker.upper(),
                model_path=settings.MODEL_PATH,
                save_dir=save_dir
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        prediction = Prediction.objects.create(
            user=request.user,
            ticker=ticker.upper(),
            predicted_price=result['predicted_price'],
            metrics={
                "mse": result['mse'],
                "rmse": result['rmse'],
                "r2": result['r2']
            },
            plot_1=f"predictions/{result['plot_1']}",
            plot_2=f"predictions/{result['plot_2']}"
        )
        data = {
            "ticker": prediction.ticker,
            "predicted_price": prediction.predicted_price,
            "metrics": {
                "mse": prediction.metrics.get("mse"),
                "rmse": prediction.metrics.get("rmse"),
                "r2": prediction.metrics.get("r2"),
            },
            "plot_1_url": settings.MEDIA_URL + prediction.plot_1.name,
            "plot_2_url": settings.MEDIA_URL + prediction.plot_2.name
        }
        return Response(data, status=201)

class PredictionListView(ListAPIView):
    serializer_class = PredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Prediction.objects.filter(user=self.request.user).order_by('-requested_at')
        ticker = self.request.query_params.get('ticker')
        date = self.request.query_params.get('date')
        if ticker:
            qs = qs.filter(ticker__iexact=ticker)
        if date:
            qs = qs.filter(requested_at__date=date)
        return qs