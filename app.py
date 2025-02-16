import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output

# Creazione di una app Dash
app = dash.Dash(__name__)
server = app.server

# Funzione che genera dati randomizzati all'apertura della pagina
def generate_data():
    # Dati temporali 
    months = pd.date_range('2024-01-01', periods=12, freq='M')
    
    base_yield = 100 # valore base del raccolto
    irrigation = 1000 # valore base irrigazione

    # Simulazione dei dati ambientali con distribuzioni normali
    temperature = np.random.normal(25, 5, 12) # media 25, deviazione 5
    humidity = np.random.normal(60, 10, 12) # media 60%, deviazione 10%
    precipitation = np.random.normal(100, 30, 12) # mm di pioggia, media 100

    # Simulazione dei dati di produzione con distribuzioni uniformi 
    growth_rate = np.random.uniform(0.8, 1.2, 12) # fattore di crescita delle colture
    fertilizer = np.random.uniform(10, 50, 12)  # kg di fertilizzante per ettaro
    selling_price = np.random.uniform(150, 300, 12)  # prezzo per tonnellata
    labor_cost = np.random.uniform(1000, 5000, 12)  # costo manodopera

    # Dati calcolati
    production = base_yield * growth_rate # produzione variabile
    yield_efficiency = production / (precipitation + fertilizer + irrigation) # efficienza del raccolto
    water_usage = precipitation + fertilizer # consumo acqua
    energy_cost = 200 + (irrigation * 2) + (temperature - 25) * 5 # costo energetico
    revenue = production * selling_price  # guadagno totale
    total_cost = labor_cost + energy_cost + fertilizer * 10  # costo totale
    profit = revenue - total_cost  # profitto netto
    soil_quality = 100 - (fertilizer * 0.2) + (precipitation * 0.1) # qualita del suolo

    # Creazione di un DataFrame
    df = pd.DataFrame({
        'Month': months,
        'Temperature': temperature,
        'Humidity': humidity,
        'Precipitation': precipitation,
        'Production': production,
        'Fertilizer' : fertilizer,
        'Irrigation' : irrigation,
        'Yield Efficiency' : yield_efficiency,
        'Water Usage' : water_usage,
        'Labor Cost' : labor_cost,
        'Energy Cost' : energy_cost,
        'Selling Price' : selling_price,
        'Revenue' : revenue,
        'Total Cost' : total_cost,
        'Profit' : profit,
        'Soil Quality' : soil_quality
    })
    
    return df

# Generazione dei dati
df = generate_data()

# Grafici
fig1 = px.line(df, x='Month', y='Production', title='Andamento della Produzione (Ton)')
fig2 = px.line(df, x='Month', y='Yield Efficiency', title='Efficienza del raccolto')
fig3 = px.area(df, x='Month', y='Water Usage', title='Utilizzo acqua')
fig4 = px.bar(df, x='Month', y='Energy Cost', title='Costo energetico (€)')
fig5 = px.line(df, x='Month', y='Profit', title='Profitto netto')
fig6 = px.density_heatmap(df, x='Month', y='Soil Quality', title='Qualità del suolo')

# Creazione del layout della dashboard 
app.layout = html.Div([
    dcc.Store(id='growth-rate-store', data={'growth_rate': list(np.random.uniform(0.8, 1.2, 12))}),  # Memorizza il valore iniziale

    html.H1("Dashboard Simulatore Ambientale e di Produzione", style={'text-align': 'center'}),
    
    # Slider per modificare condizioni metereologiche e irrigazione
    html.Div([
        html.Div([
            html.Label("Temperatura Media (°C):"),
            dcc.Slider(
                min=10, max=40, step=0.5, value=25,
                marks={i: f'{i}°' for i in range(10, 41, 5)},
                id='temperature-slider'
            ),
            html.Br(),
            html.Label("Umidità Media (%):"),
            dcc.Slider(
                min=40, max=90, step=1, value=60,
                marks={i: f'{i}%' for i in range(40, 91, 10)},
                id='humidity-slider'
            ),
            html.Br(),
            html.Label("Precipitazioni Medie (mm):"),
            dcc.Slider(
                min=10, max=200, step=1, value=100,
                marks={i: f'{i} mm' for i in range(10, 201, 30)},
                id='precipitation-slider'
            ),
            html.Br(),
            html.Label("Irrigazione (l/ha):"),
            dcc.Slider(
                min=100, max=5000, step=50, value=1000,
                marks={i: f'{i} l/ha' for i in range(100, 5100, 1000)},
                id='irrigation-slider'
            ),
        ], style={'width': '25%', 'float': 'left', 'padding': '20px'}),
        
        html.Div([
            # Grafico Produzione
            dcc.Graph(id='production-graph', figure=fig1),
            # Grafico Efficienza del Raccolto
            dcc.Graph(id='efficiency-graph', figure=fig2),
            # Grafico Utilizzo Acqua
            dcc.Graph(id='water-graph', figure=fig3),
            # Grafico Utilizzo Energetico
            dcc.Graph(id='energy-graph', figure=fig4),
            # Grafico Profitto Netto
            dcc.Graph(id='profit-graph', figure=fig5),
            # Grafico Qualita del Suolo
            dcc.Graph(id='soil-graph', figure=fig6)
        ], style={'width': '70%', 'float': 'right'})
    ])
])

# Callback per aggiornare i dati in tempo reale
@app.callback(
    [Output('production-graph', 'figure'),
     Output('efficiency-graph', 'figure'),
     Output('water-graph', 'figure'),
     Output('energy-graph', 'figure'),
     Output('profit-graph', 'figure'),
     Output('soil-graph', 'figure')],
    [Input('temperature-slider', 'value'),
     Input('humidity-slider', 'value'),
     Input('precipitation-slider', 'value'),
     Input('irrigation-slider', 'value')],  
    [dash.State('growth-rate-store', 'data')]
)

# Ricalcolo dati in base agli input
def update_simulation(temp_value, humidity_value, precipitation_value, irrigation_value, stored_data):
    global df
    df = generate_data()  # Rigenera i dati ambientali
    
    # Mantiene fisso il growth_rate preso da dcc.Store
    df['Production'] = 100 * np.array(stored_data['growth_rate'])  

    # Modifica valori in base agli slider
    df['Temperature'] += (temp_value - 25)
    df['Humidity'] += (humidity_value - 60)
    df['Precipitation'] += (precipitation_value -100)
    df['Irrigation'] += (irrigation_value - 50)  

    # Ricalcola dati
    df['Yield Efficiency'] = df['Production'] / (df['Precipitation'] + df['Fertilizer'] + df['Irrigation'])  
    df['Production'] *= (1 + (temp_value - 25) * 0.01) * (1 + (humidity_value - 60) * 0.005) * (1 + (precipitation_value - 100) * 0.002)  
    df['Water Usage'] = df['Precipitation'] + df['Fertilizer'] * 0.5  
    df['Energy Cost'] = 200 + (df['Irrigation'] * 2) + (df['Temperature'] - 25) * 5
    df['Revenue'] = df['Production'] * df['Selling Price']  
    df['Total Cost'] = df['Labor Cost'] + df['Energy Cost'] + df['Fertilizer'] * 10  
    df['Profit'] = df['Revenue'] - df['Total Cost']  #
    df['Soil Quality'] = 100 - (df['Fertilizer'] * 0.2) + (df['Precipitation'] * 0.1)
    
    # Ricalcola grafici
    fig1 = px.line(df, x='Month', y='Production', title='Andamento della Produzione (Ton)')
    fig2 = px.line(df, x='Month', y='Yield Efficiency', title='Efficienza del raccolto')
    fig3 = px.area(df, x='Month', y='Water Usage', title='Utilizzo acqua')
    fig4 = px.bar(df, x='Month', y='Energy Cost', title='Costo energetico (€)')
    fig5 = px.line(df, x='Month', y='Profit', title='Profitto netto')
    fig6 = px.density_heatmap(df, x='Month', y='Soil Quality', title='Qualità del suolo')
    
    return fig1, fig2, fig3, fig4, fig5, fig6

if __name__ == '__main__':
    app.run_server(debug=True)
