import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import requests
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from hurst import compute_Hc
import time
from threading import Thread

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Fonction pour récupérer les données de marché via l'API Binance
def fetch_market_data(symbol="BTCUSDT", interval="1m", limit=500):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data, columns=[
            "Open time", "Open", "High", "Low", "Close", "Volume",
            "Close time", "Quote asset volume", "Number of trades",
            "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"
        ])
        df["Close"] = pd.to_numeric(df["Close"], errors='coerce')
        df["Time"] = pd.to_datetime(df["Close time"], unit='ms')
        df.dropna(inplace=True)
        return df[["Time", "Close"]]
    else:
        print(f"Erreur lors de la récupération des données: {response.status_code}")
        return pd.DataFrame()

# Calcul de l'exposant de Hurst
def calculate_hurst(data):
    H, _, _ = compute_Hc(data, kind='price', simplified=True)
    return H

# Initialisation des variables globales
cryptos = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]
intervals = ["1m", "5m", "15m", "1h"]
market_data = pd.DataFrame()
current_index = 0
running = False

# Mise en page de l'application
app.layout = html.Div([
    html.H1("Analyse des Cryptomonnaies et Modélisation Fractale"),
    
    # Graphique interactif
    dcc.Graph(id='market-plot', style={'height': '70vh'}),
    
    # Exposant de Hurst et son interprétation
    html.Div([
        html.H4("Exposant de Hurst :"),
        html.Div(id='hurst-exponent', style={'font-size': '18px', 'margin-bottom': '20px'}),
        html.Div(id='hurst-interpretation', style={'font-size': '16px', 'margin-bottom': '20px'}),
    ]),
    
    # Contrôles utilisateur
    html.Div([
        html.Label("Choisissez une cryptomonnaie :"),
        dcc.Dropdown(
            id='crypto-dropdown',
            options=[{'label': crypto[:-4], 'value': crypto} for crypto in cryptos],
            value='BTCUSDT'
        ),
        
        html.Label("Intervalle de temps :"),
        dcc.Dropdown(
            id='interval-dropdown',
            options=[{'label': interval, 'value': interval} for interval in intervals],
            value='1m'
        ),
        html.Button('Start', id='start-button', n_clicks=0),
        html.Button('Pause', id='pause-button', n_clicks=0),
    ], style={'margin-top': '20px'}),
    
    # Explications mathématiques
    html.Div([
        html.H4("Explications Mathématiques :"),
        html.P(
            "Les fractales sont des objets mathématiques qui présentent une auto-similarité, "
            "c'est-à-dire que leurs motifs se répètent à différentes échelles. "
            "L'exposant de Hurst est une mesure de la mémoire ou de la tendance des séries temporelles. "
            "Il se situe entre 0 et 1 :"
        ),
        html.Ul([
            html.Li("H = 0.5 : La série est une marche aléatoire (sans tendance)."),
            html.Li("H > 0.5 : La série est persistante (les hausses ont tendance à être suivies par d'autres hausses)."),
            html.Li("H < 0.5 : La série est anti-persistante (les hausses sont suivies de baisses, et vice-versa).")
        ])
    ])
])

# Callback pour mettre à jour le graphique et calculer Hurst
@app.callback(
    [Output('market-plot', 'figure'),
     Output('hurst-exponent', 'children'),
     Output('hurst-interpretation', 'children')],
    [Input('start-button', 'n_clicks'),
     Input('pause-button', 'n_clicks'),
     Input('crypto-dropdown', 'value'),
     Input('interval-dropdown', 'value')]
)
def update_graph_and_hurst(start_clicks, pause_clicks, crypto, interval):
    global running, current_index, market_data
    
    try:
        # Gérer les actions Start/Pause
        ctx = dash.callback_context
        if ctx.triggered and 'start-button' in ctx.triggered[0]['prop_id']:
            running = True
            current_index = 0
            market_data = fetch_market_data(crypto, interval)
        elif ctx.triggered and 'pause-button' in ctx.triggered[0]['prop_id']:
            running = False

        # Afficher les données jusqu'à l'index actuel
        display_data = market_data.iloc[:current_index] if running else market_data
        hurst_value = 0.5
        if len(display_data) > 100:
            hurst_value = calculate_hurst(display_data["Close"].values)

        # Interprétation de Hurst
        if hurst_value > 0.5:
            interpretation = "La série est persistante : les hausses ou baisses ont tendance à se répéter."
        elif hurst_value < 0.5:
            interpretation = "La série est anti-persistante : les hausses sont souvent suivies de baisses."
        else:
            interpretation = "La série ressemble à une marche aléatoire : pas de tendance claire."

        # Créer le graphique
        figure = {
            'data': [
                go.Scatter(
                    x=display_data["Time"],
                    y=display_data["Close"],
                    mode='lines',
                    name=f'{crypto[:-4]} Close Price'
                )
            ],
            'layout': {
                'title': f'Prix de {crypto[:-4]} en Temps Réel',
                'xaxis': {'title': 'Temps'},
                'yaxis': {'title': 'Prix (USD)'},
            }
        }
        return figure, f"Valeur de H = {hurst_value:.2f}", interpretation

    except Exception as e:
        print(f"Erreur dans le callback : {e}")
        return {}, "Erreur", "Erreur lors du calcul de l'exposant de Hurst"

# Fonction pour simuler l'évolution des données en temps réel
def update_data():
    global running, current_index, market_data
    while True:
        if running and current_index < len(market_data):
            time.sleep(0.5)
            current_index += 1
        elif running and current_index >= len(market_data):
            running = False

# Lancer la mise à jour des données en arrière-plan
Thread(target=update_data, daemon=True).start()

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
