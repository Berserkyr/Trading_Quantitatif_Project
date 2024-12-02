import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def fetch_data(ticker, start, end):
    """Télécharge les données historiques et calcule les rendements mensuels."""
    data = yf.download(ticker, start=start, end=end)
    data['Monthly Return'] = data['Adj Close'].pct_change().resample('M').last()
    data['Month'] = data.index.month
    data['Year'] = data.index.year
    return data

def prepare_comparison_data(small_caps, large_caps):
    """Prépare les données pour une comparaison mois par mois."""
    comparison = pd.DataFrame({
        'Year': small_caps['Year'],
        'Month': small_caps['Month'],
        'Small Caps Return (%)': small_caps['Monthly Return'] * 100,
        'Large Caps Return (%)': large_caps['Monthly Return'] * 100,
    })
    comparison = comparison.dropna()
    return comparison

def visualize_3d(comparison):
    """Crée une visualisation 3D des rendements."""
    fig = px.scatter_3d(
        comparison,
        x='Month',
        y='Year',
        z='Small Caps Return (%)',
        color='Large Caps Return (%)',
        title='Comparaison des Rendements Mensuels (Small Caps vs Large Caps)',
        labels={
            'Month': 'Mois',
            'Year': 'Année',
            'Small Caps Return (%)': 'Rendement Small Caps (%)',
            'Large Caps Return (%)': 'Rendement Large Caps (%)'
        },
        color_continuous_scale=px.colors.sequential.Viridis,
    )
    fig.update_traces(marker=dict(size=6))
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Mois'),
            yaxis=dict(title='Année'),
            zaxis=dict(title='Rendement Small Caps (%)'),
        ),
        margin=dict(l=0, r=0, b=0, t=40),
    )
    fig.show()

def visualize_evolution_bar(comparison):
    """Affiche une comparaison de l'évolution des rendements entre décembre et janvier."""
    december_data = comparison[comparison['Month'] == 12]
    january_data = comparison[comparison['Month'] == 1]
    
    merged = december_data.merge(
        january_data,
        on='Year',
        suffixes=('_December', '_January')
    )

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=merged['Year'],
        y=merged['Small Caps Return (%)_January'],
        name='Small Caps (Janvier)',
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        x=merged['Year'],
        y=merged['Small Caps Return (%)_December'],
        name='Small Caps (Décembre)',
        marker_color='lightblue'
    ))
    fig.add_trace(go.Bar(
        x=merged['Year'],
        y=merged['Large Caps Return (%)_January'],
        name='Large Caps (Janvier)',
        marker_color='orange'
    ))
    fig.add_trace(go.Bar(
        x=merged['Year'],
        y=merged['Large Caps Return (%)_December'],
        name='Large Caps (Décembre)',
        marker_color='gold'
    ))

    fig.update_layout(
        title='Évolution des Rendements entre Décembre et Janvier (3 Dernières Années)',
        xaxis=dict(title='Année'),
        yaxis=dict(title='Rendements (%)'),
        barmode='group',
        bargap=0.15,
        bargroupgap=0.1
    )
    fig.show()

def main():
    # Indices représentatifs
    small_caps_ticker = '^RUT'  # Russell 2000 (Small Caps)
    large_caps_ticker = '^GSPC'  # S&P 500 (Large Caps)

    # Période d'analyse : 3 dernières années
    start_date = '2021-01-01'
    end_date = '2023-12-31'

    # Chargement des données
    small_caps_data = fetch_data(small_caps_ticker, start=start_date, end=end_date)
    large_caps_data = fetch_data(large_caps_ticker, start=start_date, end=end_date)

    # Préparation des données pour la comparaison
    comparison = prepare_comparison_data(small_caps_data, large_caps_data)

    # Visualisation 3D des rendements
    visualize_3d(comparison)

    # Évolution des rendements entre décembre et janvier
    visualize_evolution_bar(comparison)

if __name__ == "__main__":
    main()
