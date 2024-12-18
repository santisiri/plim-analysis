import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
from pathlib import Path
import dash_bootstrap_components as dbc

# Initialize the Dash app with a modern theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Feature descriptions in Spanish
FEATURE_DESCRIPTIONS = {
    'tempo': """
        El tempo representa la velocidad o ritmo de la música, medido en beats por minuto (BPM).
        Un tempo más alto indica música más rápida, mientras que un tempo más bajo sugiere música más lenta y relajada.
        Como referencia: Las baladas lentas están alrededor de 60-80 BPM, mientras que la música de baile enérgica suele estar entre 120-140 BPM.
    """,
    'spectral_centroid_mean': """
        El Centroide Espectral indica dónde está el "centro de masa" del sonido en el espectro de frecuencias.
        Valores más altos sugieren sonidos más brillantes y agudos con más frecuencias altas.
        Valores más bajos indican sonidos más profundos y graves con más frecuencias bajas.
        Esto ayuda a caracterizar el "brillo" general del audio.
    """,
    'zcr_mean': """
        La Tasa de Cruce por Cero (ZCR) mide con qué frecuencia la señal de audio cruza el punto cero.
        Valores más altos suelen indicar sonidos más percusivos o ruidosos (como consonantes en el habla o platillos en la música).
        Valores más bajos típicamente sugieren sonidos más tonales (como vocales en el habla o notas musicales sostenidas).
    """,
    'duration': """
        La duración del audio en segundos.
        Esto muestra cuánto dura la pista de audio de cada video.
    """,
    'mfcc_mean': """
        Los Coeficientes Cepstrales en las Frecuencias de Mel (MFCCs) representan el espectro de potencia a corto plazo del sonido.
        Estos coeficientes capturan el timbre y la forma general de la señal de audio.
        Patrones similares en el mapa de calor sugieren características sonoras similares entre videos.
        Esto se usa comúnmente en reconocimiento de voz y clasificación de géneros musicales.
    """,
    'views': """
        El número de visualizaciones que ha recibido cada video en YouTube.
        Esta métrica nos ayuda a entender la relación entre las características del audio y la popularidad del video.
    """
}

def load_data():
    """Load analysis results from JSON file"""
    try:
        with open(Path('results') / 'analysis_results.json', 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def create_info_card(title, description):
    """Create an info card with a title and description"""
    return dbc.Card([
        dbc.CardHeader(title),
        dbc.CardBody([
            html.P(description, className="card-text")
        ])
    ], className="mb-3")

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Panel de Análisis de Audio de YouTube", className="text-center mb-4"),
            html.P("Visualización interactiva de características de audio de videos de YouTube", className="text-center text-muted"),
            dbc.Button(
                "¿Qué significan estas métricas?",
                id="open-help",
                color="info",
                className="mb-4"
            ),
            dbc.Modal([
                dbc.ModalHeader("Entendiendo las Características del Audio"),
                dbc.ModalBody([
                    html.H5("Características de Audio Explicadas"),
                    html.Hr(),
                    *[create_info_card(feature.replace('_', ' ').title(), desc) 
                      for feature, desc in FEATURE_DESCRIPTIONS.items()]
                ]),
                dbc.ModalFooter(
                    dbc.Button("Cerrar", id="close-help", className="ml-auto")
                ),
            ], id="help-modal", size="lg", scrollable=True)
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader([
                    "Resumen de Características de Audio",
                    html.I(className="fas fa-info-circle ml-2", id="correlation-info")
                ]),
                dbc.CardBody([
                    html.P("""
                        Este mapa de calor muestra cómo se relacionan las diferentes características de audio entre sí y con el número de vistas.
                        El rojo indica correlaciones positivas (las características aumentan juntas),
                        el azul indica correlaciones negativas (cuando una aumenta, la otra disminuye).
                        Cuanto más oscuro el color, más fuerte es la relación.
                    """, className="text-muted mb-3"),
                    dcc.Graph(id='feature-correlation')
                ])
            ], className="mb-4")
        ])
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Tempo vs Vistas"),
                dbc.CardBody([
                    html.P("""
                        Este gráfico de dispersión muestra la relación entre el tempo de un video (velocidad de la música)
                        y su número de vistas. Cada punto representa un video.
                    """, className="text-muted mb-3"),
                    dcc.Graph(id='tempo-views-scatter')
                ])
            ])
        ], width=6),
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Distribución de Características"),
                dbc.CardBody([
                    html.P("""
                        Este histograma muestra con qué frecuencia ocurren diferentes valores de cada característica.
                        Usa el menú desplegable para explorar diferentes características de audio.
                    """, className="text-muted mb-3"),
                    dcc.Dropdown(
                        id='feature-selector',
                        options=[
                            {'label': 'Tempo (BPM)', 'value': 'tempo'},
                            {'label': 'Centroide Espectral (Brillo del Sonido)', 'value': 'spectral_centroid_mean'},
                            {'label': 'Tasa de Cruce por Cero (Textura del Sonido)', 'value': 'zcr_mean'},
                            {'label': 'Duración (segundos)', 'value': 'duration'}
                        ],
                        value='tempo',
                        className="mb-3"
                    ),
                    dcc.Graph(id='feature-distribution')
                ])
            ])
        ], width=6)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Patrones MFCC"),
                dbc.CardBody([
                    html.P("""
                        Este mapa de calor muestra los Coeficientes Cepstrales en las Frecuencias de Mel (MFCCs) para cada video.
                        Patrones similares (colores) indican características sonoras similares.
                        Cada fila representa un video, y cada columna representa un aspecto diferente del timbre del sonido.
                    """, className="text-muted mb-3"),
                    dcc.Graph(id='mfcc-heatmap')
                ])
            ], className="mt-4")
        ])
    ])
], fluid=True, className="p-4")

@app.callback(
    Output("help-modal", "is_open"),
    [Input("open-help", "n_clicks"), Input("close-help", "n_clicks")],
    [dash.State("help-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    Output('feature-correlation', 'figure'),
    Input('feature-selector', 'value')
)
def update_correlation_plot(_):
    df = load_data()
    if df.empty:
        return go.Figure()
    
    # Extract numeric features
    numeric_features = ['tempo', 'spectral_centroid_mean', 'zcr_mean', 'duration', 'views']
    correlation_data = df[numeric_features].corr()
    
    # Make feature names more readable in Spanish
    feature_labels = {
        'tempo': 'Tempo (BPM)',
        'spectral_centroid_mean': 'Brillo del Sonido',
        'zcr_mean': 'Textura del Sonido',
        'duration': 'Duración (s)',
        'views': 'Vistas'
    }
    
    fig = go.Figure(data=go.Heatmap(
        z=correlation_data,
        x=[feature_labels[f] for f in numeric_features],
        y=[feature_labels[f] for f in numeric_features],
        colorscale='RdBu',
        zmin=-1, zmax=1
    ))
    
    fig.update_layout(
        title="Matriz de Correlación de Características",
        height=500,
        xaxis_title="Características",
        yaxis_title="Características"
    )
    return fig

@app.callback(
    Output('tempo-views-scatter', 'figure'),
    Input('feature-selector', 'value')
)
def update_tempo_views_scatter(_):
    df = load_data()
    if df.empty:
        return go.Figure()
    
    fig = px.scatter(
        df,
        x='tempo',
        y='views',
        title='Relación entre Tempo y Vistas',
        labels={'tempo': 'Tempo (BPM)', 'views': 'Número de Vistas'},
        hover_data=['duration']
    )
    
    fig.update_traces(
        marker=dict(size=10),
        hovertemplate="<br>".join([
            "Tempo: %{x:.0f} BPM",
            "Vistas: %{y:,}",
            "Duración: %{customdata[0]:.1f} segundos"
        ])
    )
    
    return fig

@app.callback(
    Output('feature-distribution', 'figure'),
    Input('feature-selector', 'value')
)
def update_feature_distribution(feature):
    df = load_data()
    if df.empty:
        return go.Figure()
    
    # Custom labels in Spanish
    labels = {
        'tempo': 'Tempo (BPM)',
        'spectral_centroid_mean': 'Centroide Espectral (Brillo del Sonido)',
        'zcr_mean': 'Tasa de Cruce por Cero',
        'duration': 'Duración (segundos)'
    }
    
    fig = px.histogram(
        df,
        x=feature,
        nbins=10,
        title=f'Distribución de {labels[feature]}',
        labels={feature: labels[feature]}
    )
    
    fig.update_layout(
        showlegend=False,
        xaxis_title=labels[feature],
        yaxis_title="Número de Videos"
    )
    
    return fig

@app.callback(
    Output('mfcc-heatmap', 'figure'),
    Input('feature-selector', 'value')
)
def update_mfcc_heatmap(_):
    df = load_data()
    if df.empty:
        return go.Figure()
    
    # Extract MFCCs and create a matrix
    mfcc_matrix = pd.DataFrame([x for x in df['mfcc_mean']])
    
    fig = go.Figure(data=go.Heatmap(
        z=mfcc_matrix,
        colorscale='Viridis',
        hoverongaps=False,
        hovertemplate="Video: %{y}<br>MFCC %{x}: %{z:.2f}<extra></extra>"
    ))
    
    fig.update_layout(
        title="Patrones MFCC a través de los Videos",
        xaxis_title="Coeficiente MFCC (Característica del Sonido)",
        yaxis_title="Número de Video",
        height=400
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True) 