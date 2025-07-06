from django.core.management.base import BaseCommand
from predictions.utils import run_prediction
from django.conf import settings
from users.models import User
from predictions.models import Prediction
import os

class Command(BaseCommand):
    help = 'Run prediction for a ticker or all tickers'

    def add_arguments(self, parser):
        parser.add_argument('--ticker', type=str, help='Stock ticker')
        parser.add_argument('--all', action='store_true', help='Predict for all tickers in DB')

    def handle(self, *args, **options):
        if options['ticker']:
            tickers = [options['ticker']]
        elif options['all']:
            tickers = Prediction.objects.values_list('ticker', flat=True).distinct()
        else:
            self.stdout.write(self.style.ERROR('Provide --ticker or --all'))
            return

        for ticker in tickers:
            try:
                result = run_prediction(
                    ticker=ticker.upper(),
                    model_path=settings.MODEL_PATH,
                    save_dir=os.path.join(settings.MEDIA_ROOT, 'predictions')
                )
                self.stdout.write(self.style.SUCCESS(f"Predicted {ticker}: {result['predicted_price']}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error for {ticker}: {e}"))