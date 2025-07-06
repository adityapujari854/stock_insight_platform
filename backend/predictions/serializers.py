from rest_framework import serializers
from .models import Prediction

class PredictionSerializer(serializers.ModelSerializer):
    mse = serializers.SerializerMethodField()
    rmse = serializers.SerializerMethodField()
    r2 = serializers.SerializerMethodField()

    class Meta:
        model = Prediction
        fields = [
            'id', 'ticker', 'requested_at', 'predicted_price',
            'mse', 'rmse', 'r2', 'plot_1', 'plot_2'
        ]
        read_only_fields = fields

    def get_mse(self, obj):
        return obj.metrics.get('mse') if obj.metrics else None

    def get_rmse(self, obj):
        return obj.metrics.get('rmse') if obj.metrics else None

    def get_r2(self, obj):
        return obj.metrics.get('r2') if obj.metrics else None