import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
import numpy as np
import requests
from dash.dependencies import Input, Output

# Creazione di una app Dash
app = dash.Dash(__name__)
server = app.server

# Funzione per ottenere dati meteo da Open-Meteo
def ottieni_dati_meteo(citta):
    # Recupero le coordinate della città per recuperare i dati meteo
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={citta}&count=1&language=en&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            lat = data["results"][0]["latitude"]
            lon = data["results"][0]["longitude"]
            # Richiedo i dati per l'anno 2024
            meteo_url = f"https://archive-api.open-meteo.com/v1/era5?latitude={lat}&longitude={lon}&start_date=2024-01-01&end_date=2024-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=Europe/Rome"
            meteo_response = requests.get(meteo_url)
            if meteo_response.status_code == 200:
                meteo_data = meteo_response.json()
                # Creo un array con i mesi dell'anno
                mesi = np.arange(1, 13)

                # Calcolo delle temperature e delle precipitazioni medie giornaliere
                temp_giornaliera = (np.array(meteo_data['daily']['temperature_2m_max']) + np.array(meteo_data['daily']['temperature_2m_min'])) / 2
                prec_giornaliera = np.array(meteo_data["daily"]["precipitation_sum"])

                # Calcolo della temperatura, delle precipitazioni e dell'umidità media annuale
                temp_annuale = ottieni_media_temperature(temp_giornaliera)
                prec_annuale = ottieni_media_temperature(prec_giornaliera) 

                # Simulo la stagionalità della temperatura utilizzando una sinusoide per rappresentare il ciclo annuale
                ampiezza_temp = 10  # Ampiezza stagionale
                temperatura = temp_annuale + ampiezza_temp * np.sin((mesi - 3) * (2 * np.pi / 12))
                temperatura += np.random.normal(0, 1, len(mesi))  # Aggiungo un rumore casuale moderato per rendere i dati più realistici

                # Utilizzo una distribuzione mensile predefinita delle precipitazioni per rappresentare la stagionalità 
                valori_medi_prec = [800, 600, 500, 600, 700, 800, 900, 1000, 1200, 1400, 1000, 500]
                # Scalo i valori con la media annuale delle precipitazioni e aggiungo un rumore casuale moderato
                precipitazioni = (np.array(valori_medi_prec) * prec_annuale) + np.random.normal(0, 5, len(mesi))  
                precipitazioni = np.maximum(0, precipitazioni) # Applico limite inferiore a 0 per evitare valori negativi

                # Stimo l'umidità annuale usando un valore compreso tra 40% e 90%
                dist_umid_annuale = np.random.uniform(40, 90, 12)  
                # Utilizzo una sinusoide per aggiungere una lieve variazione stagionale sincronizzata con le precipitazioni
                # Aggiungo anche un rumore moderato
                ampiezza_umid = 5  # Ampiezza stagionale
                umidita = (dist_umid_annuale + ampiezza_umid * np.sin((mesi - 2) * (2 * np.pi / 12))) + np.random.normal(0, 2, len(mesi))  
                umidita = np.maximum(0, umidita) # Applico limite inferiore a 0 per evitare valori negativi
                
                return temperatura, precipitazioni, umidita
                
    return None, None, None

# Funzione che prende in input un array di temperature e restituisce la temperatura media annuale
# Definita per calcolare la media delle temperature recuperate dal servizio meteo
def ottieni_media_temperature(data):
    # Dati calcolati per l'anno 2024
    date = pd.date_range(start="2024-01-01", end="2024-12-31")
    # Creo un DataFrame Pandas con le colonne Data e Valore
    df = pd.DataFrame({'Data': date, 'Valore': data})
    df['Mese'] = df['Data'].dt.month
    # Raggruppo i dati per mese
    media_mensile = df.groupby('Mese')['Valore'].mean().values
    # Restituisce la temperatura annuale considerando le medie mensili
    return np.mean(media_mensile)


# Funzione che genera dati simulati relativi a produzione agricola su base mensile
# Utilizzo come input temperatura, precipitazioni e umidità
def genera_dati(temperatura, precipitazioni, umidita):
    # Creo un array di 12 date da utilizzare come asse temporale per i dati simulati
    mese = pd.date_range('2024-01-01', periods=12, freq='M')
    # Inizializzo i parametri principali
    irrigazione = 10 # valore iniziale irrigazione
    fertilizzante = 100 # valore iniziale fertilizzante
    prezzo_vendita = np.random.uniform(150, 300, 12)  # prezzo di vendita
    costo_manodopera = np.random.uniform(1000, 5000, 12)  # costo della manodopera
    rendimento_base = 60000 # rendimento base del raccolto
    profitto_base = 100

    # Verifico che tutti gli input siano presenti
    if temperatura is None or precipitazioni is None or umidita is None:
        return None

    # Misuro l'efficienza del raccolto rispetto a precipitazioni, fertilizzante e irrigazione
    # Più alte sono le risorse e minore è l'efficienza
    efficienza_raccolto = rendimento_base / (precipitazioni + fertilizzante + irrigazione)  
    # Misuro l'efficienza dell'uso dell'acqua tenendo conto di precipitazioni e quantità di fertilizzante utilizzato
    efficienza_acqua = efficienza_raccolto / (precipitazioni + fertilizzante)  
    # Determino quanto fertilizzante è necessario per il raccolto
    efficienza_fertilizzante = efficienza_raccolto / fertilizzante  
    # Calcolo il profitto lordo moltiplicando il profitto base per il prezzo di vendita mensile
    # Simulo variazione dei prezzi di mercato
    profitto_lordo = profitto_base * prezzo_vendita  
    # Sottraggo i costi di manodopera al profitto lordo per ottenere il profitto netto
    profitto_netto = profitto_lordo - costo_manodopera  
    # Stimo la qualità del suolo in base a fertilizzante e precipitazioni
    # L'uso del fertilizzante riduce la qualità del suolo mentre le precipitazioni la aumentano leggermente
    qualita_suolo = 100 - (fertilizzante * 0.2) + (precipitazioni * 0.1)  

    # Organizzo i dati calcolati in un DataFrame Pandas
    df = pd.DataFrame({
        'Mese': mese,
        'Temperatura': temperatura,
        'Umidita': umidita,
        'Precipitazioni': precipitazioni,
        'Efficienza Raccolto': efficienza_raccolto,
        'Efficienza Acqua': efficienza_acqua,
        'Efficienza Fertilizzante': efficienza_fertilizzante,
        'Costo Manodopera': costo_manodopera,
        'Prezzo di Vendita': prezzo_vendita,
        'Profitto Lordo': profitto_lordo,
        'Profitto Netto': profitto_netto,
        'Qualita del suolo': qualita_suolo
    })
    
    return df

# Strutturo il layout della dashboard con Dash
app.layout = html.Div([
    # Memorizzo un fattore di crescita casuale per ogni mese dell'anno
    # Serve per mantenere lo stato durante le interazioni
    dcc.Store(id='fattore-crescita-store', data={'fattore-crescita': list(np.random.uniform(0.8, 1.2, 12))}),  # Memorizza il valore iniziale

    # Titolo
    html.H1("Dashboard Simulatore Ambientale e di Produzione", style={'text-align': 'center', 'font-weight': 'bold', 'font-family': 'Helvetica'}),

    html.Div([
        html.Div([
            html.Div([
                # Input città e informazioni meteo
                html.Label("Inserisci la tua città: ", style={'font-weight': 'bold'}),
                dcc.Input(id='citta-input', type='text', placeholder='Es. Roma, Milano...'),
                html.Button('Aggiorna', id='update-button', n_clicks=0),
                html.Div(id='msg-errore', style={'color': 'red'}),
                html.Br(),
                html.Div(id='info-citta'),
                html.Br(),
                html.Div(id='info-temperatura'),
                html.Br(),
                html.Div(id='info-precipitazioni'),
                html.Br(),
                html.Div(id='info-umidita'),
                html.Br()], style={'padding': '20px', 'font-family': 'Helvetica'}),
            html.Div([
                # Slider per irrigazione e fertilizzante
                html.Div([
                html.Label("Irrigazione (l/ha):", style={'font-family': 'Verdana', 'padding': '20px'}),
                dcc.Slider(
                    min=100, max=5000, step=5, value=1000, # Step e valori massimi realistici per il contesto
                    marks={i: f'{i}' for i in range(0, 5000, 500)}, # Mostro le etichette dell'unità di misura sui valori principali
                    id='slider-irrigazione'
                )], style={'margin-bottom': '50px'}),
                html.Label("Fertilizzante (Kg/ha):", style={'font-family': 'Verdana', 'padding': '20px'}),
                dcc.Slider(
                    min=10, max=1000, step=10, value=500, # Step e valori massimi realistici per il contesto
                    marks={i: f'{i}' for i in range(0, 1000, 100)}, # Mostro le etichette dell'unità di misura sui valori principali
                    id='slider-fertilizzante')
                ]),
        ], style={'width': '25%', 'float': 'left', 'padding': '20px'}),

    # Creo i grafici interattivi
    html.Div([
                # Grafico Efficienza del Raccolto
                dcc.Graph(id='grafico-efficienza-raccolto'),
                # Grafico Utilizzo Acqua
                dcc.Graph(id='grafico-utilizzo-acqua'),
                # Grafico Utilizzo Fertilizzante
                dcc.Graph(id='grafico-utilizzo-fertilizzante'),
                # Grafico Profitto Netto
                dcc.Graph(id='grafico-profitto-netto'),
                # Grafico Qualita del Suolo
                dcc.Graph(id='grafico-qualita-suolo')
            ], style={'width': '70%', 'float': 'right'})
        ])
    ])

# Callback per aggiornare i dati
@app.callback(
    [Output('grafico-efficienza-raccolto', 'figure'),
     Output('grafico-utilizzo-acqua', 'figure'),
     Output('grafico-utilizzo-fertilizzante', 'figure'),
     Output('grafico-profitto-netto', 'figure'),
     Output('grafico-qualita-suolo', 'figure'),
     Output('msg-errore', 'children'),
     Output('info-citta', 'children'),
     Output('info-temperatura', 'children'),
     Output('info-precipitazioni', 'children'),
     Output('info-umidita', 'children')],
    [Input('update-button', 'n_clicks'),
     Input('slider-irrigazione', 'value'),
     Input('slider-fertilizzante', 'value')],
    [dash.State('citta-input', 'value'),
     dash.State('fattore-crescita-store', 'data')]
)

# Funzione di callback principale
# Viene richiamata ogni volta che si clicca il bottone di aggiornamento (n_clicks) o si modificano gli slider
def update_dashboard(n_clicks, valore_irrigazione, valore_fertilizzante, citta, stored_data):
    if n_clicks > 0 and citta:
        temperatura, precipitazioni, umidita = ottieni_dati_meteo(citta)
        
        # Se i dati meteo sono disponibili genero il DataFrame contenente i dati
        if temperatura is not None and precipitazioni is not None and umidita is not None:
            df = genera_dati(temperatura, precipitazioni, umidita)
            
            # Se il DataFrame è stato creato correttamente mostro la città e le statistiche meteo
            if df is not None:
                info_citta = f"Città: {citta.capitalize()}" # Prima lettera della città maiuscola
                # Utilizzo np.mean() per mostrare le medie annuali
                info_temperatura = f"Temperatura Media Annuale: {np.mean(temperatura):.2f}°C"
                info_precipitazioni = f"Precipitazioni Medie Annuali: {np.mean(precipitazioni):.2f} mm"
                info_umidita = f"Umidità Media Annuale: {np.mean(umidita):.2f}%"

                # Mantengo fisso il fattore-crescita preso da dcc.Store
                df['Produzione'] = 100 * np.array(stored_data['fattore-crescita'])  

                # Modifico i valori in base agli slider
                # Offset 50 e 100 regolano i dati in modo più realistico
                df['Irrigazione'] += (valore_irrigazione - 50)  
                df['Fertilizzante'] += (valore_fertilizzante - 100)
                
                # Creo i grafici interattivi con Plotly Express
                fig2 = px.line(df, x='Mese', y='Efficienza Raccolto', title='Efficienza del raccolto (Kg/ha)')
                fig3 = px.bar(df, x='Mese', y='Efficienza Acqua', title='Efficienza Utilizzo Idrico (Kg/litro)')
                fig4 = px.bar(df, x='Mese', y='Efficienza Fertilizzante', title='Efficienza Utilizzo Fertilizzante (Kg/Kg di fertilizzante)')
                fig5 = px.line(df, x='Mese', y='Profitto Netto', title='Profitto netto (€)')
                fig6 = px.density_heatmap(df, x='Mese', y='Qualita del suolo', title='Qualità del suolo')
                
                # Restituisco i grafici e le stringhe aggiornate senza messaggio di errore
                return fig2, fig3, fig4, fig5, fig6, "", info_citta, info_temperatura, info_precipitazioni, info_umidita  
            
            # Se il DataFrame è None (es. errore durante la generazione dei dati) mostro messaggio di errore e grafici vuoti
            else:
                msg_errore = "Errore durante la generazione dei dati. Riprova."
                figura_vuota = px.line(title="Dati non disponibili")
                return  figura_vuota, figura_vuota, figura_vuota, figura_vuota, figura_vuota, msg_errore, "", "", "", ""
        
        # Se la città non viene trovata o i dati meteo non sono disponibili mostro messaggio di errore specifico
        else:
            msg_errore = "Città non trovata o dati meteo non disponibili."
            figura_vuota = px.line(title="Dati non disponibili")
            return figura_vuota, figura_vuota, figura_vuota, figura_vuota, figura_vuota, msg_errore, "", "", "", ""
    
    # Se l'utente non ha ancora cliccato o non ha inserito la città
    figura_vuota = px.line(title="Dati non disponibili")
    return figura_vuota, figura_vuota, figura_vuota, figura_vuota, figura_vuota, "", "", "", "", ""

# Avvio il server Dash in modalità debug
if __name__ == '__main__':
    app.run_server(debug=True)
