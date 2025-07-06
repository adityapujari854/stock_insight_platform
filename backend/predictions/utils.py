import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model
from django.conf import settings
import os
from sklearn.metrics import mean_squared_error, r2_score

def run_prediction(ticker, model_path, save_dir):
    df = yf.download(ticker, period="5y")
    if df.empty or len(df) < 101:
        raise ValueError("Not enough data to predict.")

    close_prices = df['Close'].values

    # Min-Max Scaling
    min_, max_ = close_prices.min(), close_prices.max()
    scaled_prices = (close_prices - min_) / (max_ - min_)

    # Create sliding windows of 100 days
    X = []
    y_true = []
    for i in range(100, len(scaled_prices)):
        X.append(scaled_prices[i-100:i])
        y_true.append(scaled_prices[i])
    X = np.array(X).reshape(-1, 100, 1)
    y_true = np.array(y_true)

    # Load model
    model = load_model(model_path)

    # Predict
    y_pred_scaled = model.predict(X)
    y_pred = y_pred_scaled.flatten() * (max_ - min_) + min_
    y_true_rescaled = y_true * (max_ - min_) + min_

    # Metrics
    mse = float(mean_squared_error(y_true_rescaled, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true_rescaled, y_pred))

    # Predict next day using last 100 prices
    last_100 = scaled_prices[-100:].reshape(1, 100, 1)
    next_pred_scaled = model.predict(last_100)
    next_pred = float(next_pred_scaled.flatten()[0] * (max_ - min_) + min_)

    # Plot 1: Actual vs Predicted
    plt.figure(figsize=(10, 5))
    plt.plot(df.index[100:], y_true_rescaled, label='Actual')
    plt.plot(df.index[100:], y_pred, label='Predicted')
    plt.title(f"{ticker} Prediction")
    plt.legend()
    plot1_name = f"{ticker.lower()}_plot1.png"
    plot1_path = os.path.join(save_dir, plot1_name)
    plt.savefig(plot1_path)
    plt.close()

    # Plot 2: Error (Residuals)
    plt.figure(figsize=(10, 5))
    residuals = y_true_rescaled - y_pred
    plt.plot(df.index[100:], residuals, label='Residuals', color='red')
    plt.title(f"{ticker} Prediction Error")
    plt.legend()
    plot2_name = f"{ticker.lower()}_plot2.png"
    plot2_path = os.path.join(save_dir, plot2_name)
    plt.savefig(plot2_path)
    plt.close()

    return {
        "predicted_price": next_pred,
        "mse": mse,
        "rmse": rmse,
        "r2": r2,
        "plot_1": plot1_name,
        "plot_2": plot2_name
    }
