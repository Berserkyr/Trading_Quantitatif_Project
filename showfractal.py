import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import time
from threading import Thread

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Générer des données initiales (séries fractales simulées)
def generate_fractal_series(length=1000):
    np.random.seed(42)
    return np.cumsum(np.random.randn(length))

# Données initiales
data_length = 500
data = generate_fractal_series(data_length)
time_indices = list(range(data_length))

# Mise en page de l'application
app.layout = html.Div([
    html.H1("Modélisation Interactive des Séries Fractales"),
    
    # Graphique interactif
    dcc.Graph(id='fractal-plot', style={'height': '70vh'}),
    
    # Contrôles pour l'utilisateur
    html.Div([
        html.Label("Échelle de temps (en points):"),
        dcc.Slider(
            id='scale-slider',
            min=50,
            max=1000,
            step=50,
            value=500,
            marks={i: str(i) for i in range(50, 1001, 200)},
        ),
        html.Button('Start', id='start-button', n_clicks=0),
        html.Button('Pause', id='pause-button', n_clicks=0),
    ], style={'margin-top': '20px'}),
])

# Variables globales pour le mode "Start/Pause"
running = False
current_index = 0

# Fonction pour mettre à jour le graphique
@app.callback(
    Output('fractal-plot', 'figure'),
    [Input('scale-slider', 'value'),
     Input('start-button', 'n_clicks'),
     Input('pause-button', 'n_clicks')]
)
def update_graph(scale, start_clicks, pause_clicks):
    global running, current_index, data, time_indices
    
    # Gestion du démarrage et de la pause
    ctx = dash.callback_context
    if ctx.triggered and 'start-button' in ctx.triggered[0]['prop_id']:
        running = True
    elif ctx.triggered and 'pause-button' in ctx.triggered[0]['prop_id']:
        running = False
    
    # Afficher les données jusqu'à l'index actuel
    display_data = data[:current_index] if running else data[:scale]
    display_time = time_indices[:current_index] if running else time_indices[:scale]
    
    # Créer le graphique
    figure = {
        'data': [
            go.Scatter(
                x=display_time,
                y=display_data,
                mode='lines',
                name='Série Fractale'
            )
        ],
        'layout': {
            'title': 'Évolution des Séries Fractales',
            'xaxis': {'title': 'Temps'},
            'yaxis': {'title': 'Valeur'},
        }
    }
    return figure

# Fonction pour faire évoluer les données automatiquement
def update_data():
    global running, current_index, data_length, data
    while True:
        if running:
            time.sleep(0.1)  # Pause pour simuler l'évolution
            if current_index < data_length:
                current_index += 1
            else:
                running = False

# Lancer la mise à jour des données dans un thread séparé
Thread(target=update_data, daemon=True).start()

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
