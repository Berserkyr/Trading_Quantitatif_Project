import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Télécharger les données de NVIDIA sur les 3 derniers mois
def download_market_data(ticker, period="3mo", interval="1d"):
    """
    Télécharge les données de marché pour un actif donné.
    Args:
        ticker (str): Symbole de l'action (ex: 'NVDA').
        period (str): Période (ex: '3mo' pour 3 mois).
        interval (str): Intervalle de temps (ex: '1d' pour quotidien).
    Returns:
        pd.DataFrame: Données du marché.
    """
    data = yf.download(ticker, period=period, interval=interval)
    print(data.head())  # Vérifie les premières lignes des données
    print(data.columns)  # Vérifie les colonnes disponibles
    if 'High' not in [col[0] for col in data.columns]:
        raise ValueError("La colonne 'High' est absente des données téléchargées.")
    # Aplatir les colonnes
    data.columns = ['_'.join(col) for col in data.columns]
    return data

# Identifier les fractales baissières
def find_bearish_fractals(data):
    """
    Identifie les fractales baissières dans les données de marché.
    Args:
        data (pd.DataFrame): Données de marché.
    Returns:
        pd.DataFrame: Données avec une colonne indiquant les fractales baissières.
    """
    data['Bearish_Fractal'] = 0  # Initialisation de la colonne des fractales baissières
    
    for i in range(2, len(data) - 2):
        current_high = data.at[data.index[i], 'High_NVDA']
        prev_high_1 = data.at[data.index[i - 1], 'High_NVDA']
        prev_high_2 = data.at[data.index[i - 2], 'High_NVDA']
        next_high_1 = data.at[data.index[i + 1], 'High_NVDA']
        next_high_2 = data.at[data.index[i + 2], 'High_NVDA']
        
        if current_high > prev_high_1 and current_high > prev_high_2 and current_high > next_high_1 and next_high_2:
            data.at[data.index[i], 'Bearish_Fractal'] = 1  # Marquer la fractale baissière
    
    return data

# Visualiser les fractales baissières
def plot_bearish_fractals(data, ticker):
    """
    Visualise les fractales baissières sur un graphique.
    Args:
        data (pd.DataFrame): Données de marché avec fractales baissières.
        ticker (str): Symbole de l'actif.
    """
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close_NVDA'], label=f'{ticker} - Prix de clôture', alpha=0.8)
    # Ajouter les fractales baissières sur le graphique
    bearish_fractals = data[data['Bearish_Fractal'] == 1]
    plt.scatter(bearish_fractals.index, bearish_fractals['High_NVDA'], label='Fractales Baissières', color='red', marker='v')
    
    plt.title(f'Fractales Baissières pour {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Prix')
    plt.legend()
    plt.show()

# Exemple d'utilisation
if __name__ == "__main__":
    ticker = "NVDA"  # Symbole de NVIDIA
    data = download_market_data(ticker, period="3mo", interval="1d")
    data = find_bearish_fractals(data)
    plot_bearish_fractals(data, ticker)
