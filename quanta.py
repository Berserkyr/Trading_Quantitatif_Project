import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Fonction pour récupérer les données
def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data['Close']

# Calcul de l'effet Momentum
def calculate_momentum(data, window):
    momentum = data.diff(window)
    return momentum

# Calcul du retour à la moyenne
def calculate_mean_reversion(data, window):
    rolling_mean = data.rolling(window).mean()
    deviation = data - rolling_mean
    return deviation

# Analyse et visualisation
def analyze_stock(ticker, start_date, end_date, momentum_window, mean_reversion_window):
    # Récupérer les données
    data = fetch_data(ticker, start_date, end_date)

    # Calculer Momentum et Retour à la moyenne
    momentum = calculate_momentum(data, momentum_window)
    mean_reversion = calculate_mean_reversion(data, mean_reversion_window)

    # Visualiser les résultats
    plt.figure(figsize=(14, 8))
    plt.plot(data, label="Prix de clôture", linewidth=2)
    plt.plot(data.rolling(mean_reversion_window).mean(), label=f"Moyenne mobile ({mean_reversion_window} jours)", linestyle='--')
    plt.scatter(data.index, data[momentum > 0], color='green', label="Momentum positif", alpha=0.6)
    plt.scatter(data.index, data[momentum < 0], color='red', label="Momentum négatif", alpha=0.6)
    plt.title(f"Analyse de {ticker}: Momentum et Retour à la Moyenne")
    plt.xlabel("Date")
    plt.ylabel("Prix")
    plt.legend()
    plt.grid()
    plt.show()

# Paramètres
ticker = "AAPL"  # Exemple : action Apple
start_date = "2020-01-01"
end_date = "2023-01-01"
momentum_window = 5  # Nombre de jours pour calculer le momentum
mean_reversion_window = 20  # Fenêtre pour la moyenne mobile

# Lancer l'analyse
analyze_stock(ticker, start_date, end_date, momentum_window, mean_reversion_window)
