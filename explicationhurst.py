import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objs as go
from hurst import compute_Hc

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Fonction pour générer une série temporelle fractale simulée
def generate_fractal_series(length=500):
    np.random.seed(42)
    return np.cumsum(np.random.randn(length))

# Fonction pour calculer l'exposant de Hurst avec les données nécessaires pour la visualisation
def calculate_hurst_with_visualization(data):
    """Retourne l'exposant de Hurst et les données log-log nécessaires."""
    H, c, tau = compute_Hc(data, kind='price', simplified=False)
    scales = 2 ** np.arange(2, len(tau) + 2)  # Échelles (2^n)
    fluctuations = np.exp(tau)  # Fluctuations associées
    return H, scales, fluctuations

# Générer les données initiales
data_length = 500
series = generate_fractal_series(data_length)
H, scales, fluctuations = calculate_hurst_with_visualization(series)

# Mise en page de l'application
app.layout = html.Div([
    html.H1("Exposant de Hurst : Visualisation Interactive"),
    
    # Graphique interactif
    dcc.Graph(id='hurst-plot', style={'height': '70vh'}),
    
    # Contrôle utilisateur pour ajuster la longueur de la série
    html.Div([
        html.Label("Longueur de la série temporelle :"),
        dcc.Slider(
            id='series-length-slider',
            min=100,
            max=1000,
            step=50,
            value=500,
            marks={i: str(i) for i in range(100, 1001, 200)},
        )
    ], style={'margin-top': '20px'}),
    
    # Résultats de l'exposant de Hurst
    html.Div([
        html.H4("Exposant de Hurst Calculé :"),
        html.Div(id='hurst-value', style={'font-size': '18px', 'margin-bottom': '20px'}),
    ])
])

# Callback pour mettre à jour les graphiques et les calculs
@app.callback(
    [Output('hurst-plot', 'figure'),
     Output('hurst-value', 'children')],
    [Input('series-length-slider', 'value')]
)
def update_hurst_visualization(length):
    # Générer une nouvelle série temporelle
    series = generate_fractal_series(length)
    H, scales, fluctuations = calculate_hurst_with_visualization(series)

    # Préparer les graphiques
    fig = go.Figure()

    # Série temporelle
    fig.add_trace(go.Scatter(
        x=np.arange(len(series)),
        y=series,
        mode='lines',
        name='Série Temporelle'
    ))

    # Log-log plot (visualisation de Hurst)
    log_scales = np.log2(scales)
    log_fluctuations = np.log2(fluctuations)

    fig.add_trace(go.Scatter(
        x=log_scales,
        y=log_fluctuations,
        mode='markers+lines',
        name='Log-Log Plot (Hurst)',
        line=dict(dash='dot')
    ))

    # Régression linéaire pour Hurst
    intercept = log_fluctuations[0] - H * log_scales[0]
    regression_line = H * log_scales + intercept
    fig.add_trace(go.Scatter(
        x=log_scales,
        y=regression_line,
        mode='lines',
        name='Régression Linéaire (H)',
        line=dict(dash='dash', color='red')
    ))

    # Mettre à jour la disposition du graphique
    fig.update_layout(
        title="Visualisation de l'Exposant de Hurst",
        xaxis_title="Échelle (log2)",
        yaxis_title="Fluctuations (log2)",
        legend_title="Graphiques",
        height=600
    )
    return fig, f"Exposant de Hurst Calculé : H = {H:.2f}"

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
