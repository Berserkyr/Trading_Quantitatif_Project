# Importation des bibliothèques nécessaires
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Étape 1 : Télécharger les données financières
def download_data(ticker, start_date, end_date):
    """
    Télécharge les données de marché pour un actif donné.
    Args:
        ticker (str): Le symbole de l'action (ex: 'AAPL').
        start_date (str): Date de début ('YYYY-MM-DD').
        end_date (str): Date de fin ('YYYY-MM-DD').
    Returns:
        pd.DataFrame: Données de marché avec les prix de clôture.
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    data['Return'] = data['Close'].pct_change()  # Calcul des rendements quotidiens
    return data

# Étape 2 : Calcul des moyennes mobiles
def calculate_moving_averages(data, short_window, long_window):
    """
    Calcule les moyennes mobiles (SMA) pour identifier les tendances.
    Args:
        data (pd.DataFrame): Données de marché.
        short_window (int): Fenêtre pour la SMA courte.
        long_window (int): Fenêtre pour la SMA longue.
    Returns:
        pd.DataFrame: Données avec SMA ajoutées.
    """
    data['SMA_Short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_Long'] = data['Close'].rolling(window=long_window).mean()
    return data

# Étape 3 : Génération des signaux de trading
def generate_signals(data):
    """
    Génère des signaux d'achat et de vente basés sur les croisements de SMA.
    Args:
        data (pd.DataFrame): Données avec SMA.
    Returns:
        pd.DataFrame: Données avec signaux ajoutés.
    """
    data['Signal'] = 0  # Initialiser la colonne des signaux
    # Signal d'achat : SMA courte dépasse SMA longue
    data.loc[data['SMA_Short'] > data['SMA_Long'], 'Signal'] = 1
    # Signal de vente : SMA longue dépasse SMA courte
    data.loc[data['SMA_Short'] <= data['SMA_Long'], 'Signal'] = -1
    return data

# Étape 4 : Visualisation des signaux
def plot_results(data, ticker):
    """
    Trace les prix et les moyennes mobiles avec les signaux d'achat et de vente.
    Args:
        data (pd.DataFrame): Données avec signaux.
        ticker (str): Symbole de l'actif.
    """
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label=f'{ticker} - Prix de clôture', alpha=0.5)
    plt.plot(data['SMA_Short'], label='Moyenne mobile courte (SMA)', linestyle='--')
    plt.plot(data['SMA_Long'], label='Moyenne mobile longue (SMA)', linestyle='--')

    # Ajouter les signaux d'achat (vert) et de vente (rouge)
    buy_signals = data[data['Signal'] == 1]
    sell_signals = data[data['Signal'] == -1]
    plt.scatter(buy_signals.index, buy_signals['Close'], label='Signal Achat', marker='^', color='green', alpha=1)
    plt.scatter(sell_signals.index, sell_signals['Close'], label='Signal Vente', marker='v', color='red', alpha=1)

    plt.title('Signaux de Trading basés sur les Moyennes Mobiles')
    plt.xlabel('Date')
    plt.ylabel('Prix')
    plt.legend()
    plt.show()

# Exemple d'utilisation
if __name__ == "__main__":
    # Paramètres de configuration
    ticker = "AAPL"  # Symbole de l'action (Apple dans cet exemple)
    start_date = "2022-01-01"
    end_date = "2023-01-01"
    short_window = 10  # SMA courte (10 jours)
    long_window = 50  # SMA longue (50 jours)

    # Exécution des étapes
    data = download_data(ticker, start_date, end_date)
    data = calculate_moving_averages(data, short_window, long_window)
    data = generate_signals(data)

    # Visualiser les résultats
    plot_results(data, ticker)
