from django.db import models
from django.conf import settings

class Prediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ticker = models.CharField(max_length=10)
    requested_at = models.DateTimeField(auto_now_add=True)
    predicted_price = models.FloatField()
    metrics = models.JSONField()
    plot_1 = models.ImageField(upload_to='predictions/')
    plot_2 = models.ImageField(upload_to='predictions/')

    def __str__(self):
        return f"{self.ticker} - {self.predicted_price:.2f} ({self.requested_at:%Y-%m-%d})"