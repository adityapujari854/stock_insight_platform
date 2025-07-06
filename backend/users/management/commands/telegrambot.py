from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from django.conf import settings
from users.models import TelegramUser, User, UserProfile
from predictions.utils import run_prediction
from predictions.models import Prediction
from asgiref.sync import sync_to_async
import os
from datetime import datetime

class Command(BaseCommand):
    help = "Run the Telegram bot using long polling"

    # ───── Async-safe ORM operations ─────
    @sync_to_async
    def get_or_create_user(self, user_id, chat_id):
        user, _ = User.objects.get_or_create(username=f"tg_{user_id}")
        TelegramUser.objects.update_or_create(chat_id=chat_id, defaults={"user": user})
        return user

    @sync_to_async
    def get_telegram_user(self, chat_id):
        return TelegramUser.objects.filter(chat_id=chat_id).first()

    @sync_to_async
    def get_latest_prediction(self, user):
        return Prediction.objects.filter(user=user).order_by('-requested_at').first()

    @sync_to_async
    def check_quota(self, user):
        profile = UserProfile.objects.get(user=user)
        if profile.is_pro:
            return True, profile.daily_quota, 0
        today = datetime.utcnow().date()
        count = Prediction.objects.filter(user=user, requested_at__date=today).count()
        return count < profile.daily_quota, profile.daily_quota, count

    # ───── Handlers ─────
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.get_or_create_user(update.effective_user.id, update.effective_chat.id)
        await update.message.reply_text("Welcome! Use /predict <TICKER> to get started.")

    async def help_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "/predict <TICKER> - Predict next-day price\n"
            "/latest - Show your latest prediction"
        )

    async def predict_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        args = context.args
        if not args:
            await update.message.reply_text("Usage: /predict <TICKER>")
            return

        ticker = args[0].upper()
        tg_user = await self.get_telegram_user(update.effective_chat.id)
        if not tg_user:
            await update.message.reply_text("Please use /start first.")
            return

        # Quota check
        allowed, quota, used = await self.check_quota(tg_user.user)
        if not allowed:
            await update.message.reply_text(
                f"Daily quota exceeded ({used}/{quota}). Upgrade to Pro at https://yourdomain.com/subscribe/"
            )
            return

        save_dir = os.path.join(settings.MEDIA_ROOT, 'predictions')
        os.makedirs(save_dir, exist_ok=True)

        try:
            result = run_prediction(
                ticker=ticker,
                model_path=settings.MODEL_PATH,
                save_dir=save_dir
            )
            await update.message.reply_text(
                f"{ticker} predicted price: {result['predicted_price']:.2f}\n"
                f"MSE: {result['mse']:.4f}\n"
                f"RMSE: {result['rmse']:.4f}\n"
                f"R2: {result['r2']:.4f}"
            )
            await update.message.reply_photo(photo=open(os.path.join(save_dir, result['plot_1']), 'rb'))
            await update.message.reply_photo(photo=open(os.path.join(save_dir, result['plot_2']), 'rb'))
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")

    async def latest_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        tg_user = await self.get_telegram_user(update.effective_chat.id)
        if not tg_user:
            await update.message.reply_text("Please use /start first.")
            return

        pred = await self.get_latest_prediction(tg_user.user)
        if not pred:
            await update.message.reply_text("No predictions found.")
            return

        await update.message.reply_text(
            f"Latest: {pred.ticker} predicted price: {pred.predicted_price:.2f}\n"
            f"MSE: {pred.metrics['mse']:.4f}\n"
            f"RMSE: {pred.metrics['rmse']:.4f}\n"
            f"R2: {pred.metrics['r2']:.4f}"
        )
        await update.message.reply_photo(photo=open(pred.plot_1.path, 'rb'))
        await update.message.reply_photo(photo=open(pred.plot_2.path, 'rb'))

    # ───── Entry point ─────
    def handle(self, *args, **options):
        app = ApplicationBuilder().token(settings.BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_cmd))
        app.add_handler(CommandHandler("predict", self.predict_cmd))
        app.add_handler(CommandHandler("latest", self.latest_cmd))

        self.stdout.write(self.style.SUCCESS("✅ Telegram Bot is running..."))
        app.run_polling()
