import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# Télécharger les données financières
data = yf.download("AAPL", start="2022-01-01", end="2023-01-01")

# Détecter les fractales
def detect_fractals(data):
    """
    Identifie les fractales haussières et baissières dans les données.
    Args:
        data (pd.DataFrame): Données financières avec prix haut et bas.
    Returns:
        pd.DataFrame: Données avec colonnes 'Fractal_Up' et 'Fractal_Down'.
    """
    data['Fractal_Up'] = (data['High'].shift(2) > data['High'].shift(1)) & \
                         (data['High'].shift(2) > data['High']) & \
                         (data['High'].shift(2) > data['High'].shift(-1)) & \
                         (data['High'].shift(2) > data['High'].shift(-2))
    
    data['Fractal_Down'] = (data['Low'].shift(2) < data['Low'].shift(1)) & \
                           (data['Low'].shift(2) < data['Low']) & \
                           (data['Low'].shift(2) < data['Low'].shift(-1)) & \
                           (data['Low'].shift(2) < data['Low'].shift(-2))
    
    return data

# Appliquer la détection des fractales
data = detect_fractals(data)

# Visualiser les fractales sur un graphique
plt.figure(figsize=(14, 7))
plt.plot(data['Close'], label="Prix de clôture", alpha=0.5, linewidth=1)
plt.scatter(data[data['Fractal_Up']].index, data[data['Fractal_Up']]['High'], 
            label='Fractale Haussière', color='green', marker='^', s=100)
plt.scatter(data[data['Fractal_Down']].index, data[data['Fractal_Down']]['Low'], 
            label='Fractale Baissière', color='red', marker='v', s=100)

# Ajouter des titres et légendes
plt.title('Détection des Fractales sur les Prix de AAPL', fontsize=16)
plt.xlabel('Date', fontsize=12)
plt.ylabel('Prix ($)', fontsize=12)
plt.legend()
plt.grid(True)
plt.show()
