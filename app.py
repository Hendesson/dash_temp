"""
Dashboard Temperaturas Diárias - Geocalor
Versão leve e independente para visualização de temperaturas
"""
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import os
import logging
import pandas as pd
from data_processing import DataProcessor
from visualization import Visualizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
    ]
)
server = app.server
app.title = "Dashboard de Ondas de Calor - Temperaturas Diárias"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def get_image_url(app, image_name: str) -> str:
    return app.get_asset_url(image_name)

# Inicialização dos processadores
try:
    data_processor = DataProcessor()
    visualizer = Visualizer()
    df = data_processor.load_data()
    cidades = data_processor.cidades if data_processor.cidades else []
    anos = data_processor.anos if data_processor.anos else []
    if not isinstance(cidades, list):
        cidades = []
    if not isinstance(anos, list):
        anos = []
    logger.info(f"Dados inicializados: {len(df)} linhas, {len(cidades)} cidades, {len(anos)} anos")
except Exception as e:
    logger.error(f"Erro ao inicializar dados: {e}")
    df = pd.DataFrame()
    cidades = []
    anos = []
    data_processor = None
    visualizer = Visualizer()

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Img(src=app.get_asset_url('geocalor.png'), className="logo-img"),
            html.H2("Dashboard de Ondas de Calor - Temperaturas Diárias", className="text-center my-4")
        ], width=12)
    ], align="center"),
    html.Br(),
    html.Label("Selecione o período:"),
    dcc.RangeSlider(
        id="slider-anos",
        min=min(anos) if anos and len(anos) > 0 else 1981,
        max=2023,
        step=1,
        marks={int(a): str(a) for a in anos[::2]} if anos and len(anos) > 0 else {1981: "1981", 2023: "2023"},
        value=[min(anos), 2023] if anos and len(anos) > 0 else [1981, 2023]
    ),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Estações Meteorológicas Utilizadas")),
                dbc.CardBody([
                    dl.Map([
                        dl.TileLayer(),
                        dl.LayerGroup([
                            dl.Marker(position=(row["Lat"], row["Long"]),
                                      children=dl.Tooltip(row["cidade"]))
                            for _, row in df.drop_duplicates("cidade")[["cidade", "Lat", "Long"]].iterrows()
                        ]) if not df.empty and "Lat" in df.columns and "Long" in df.columns and len(df) > 0 else []
                    ], style={"width": "100%", "height": "400px"},
                       center=(df["Lat"].mean(), df["Long"].mean()) if not df.empty and len(df) > 0 and "Lat" in df.columns and "Long" in df.columns else (-15, -50), zoom=3),
                ])
            ]),
            dbc.Card([
                dbc.CardBody([
                    html.H5("Metodologia", className="card-title"),
                    html.P([
                        "Nesse Projeto estamos utilizando o Fator de Excesso de Calor (EHF – Excess Heat Factor) para definir as Ondas de Calor e classifica-las em relação intensidade. O EHF é um cálculo desenvolvido por Nairn e Fawcett em 2015 e já foi testado e aprovado para uso no mundo todo, inclusive em muitos estudos no Brasil e até por secretarias de saúde estatais. Os cálculos do EHF levam em conta as características locais e fazem uma média entre um período de vários anos anteriores e dos 30 dias anteriores, pois esse é, aproximadamente, o tempo que o corpo leva para se adaptar às temperaturas. Ou seja, se a temperatura subir muito rapidamente, as pessoas não conseguirão se adaptar às condições extremas e os impactos podem ser mais graves. Por conta dessa característica, o EHF é recomendado para estudos sobre Ondas de Calor e Saúde. As fórmulas utilizadas podem ser vistas abaixo, mas para acessar o artigo original, você pode ",
                        html.A("clicar aqui", href="https://www.mdpi.com/1660-4601/12/1/227", target="_blank"),
                        "."
                    ], className="card-text"),
                    html.Div([
                        html.P("T95 = percentil 95 das temperaturas médias diárias para o período de referência (30 anos).", className="mb-2"),
                        html.P("Ti = temperatura média diária do dia i.", className="mb-2"),
                        html.P("EHIsig = ((Ti + Ti+1 + Ti+2) / 3) – T95", className="mb-2"),
                        html.P("EHIaccl = ((Ti + Ti+1 + Ti+2) / 3) - ((Ti-1 + ... + Ti-30) / 30)", className="mb-2"),
                        html.P("EHF = EHIsig * max(1, EHIaccl)", className="mb-4")
                    ], className="mt-3"),
                    html.H5("DADOS", className="card-title mt-4 mb-2 text-center"),
                    dbc.Row([
                        dbc.Col([
                            html.Img(src=get_image_url(app, 'inmet.png'), style={'height': '50px', 'width': 'auto'}, className="mx-auto d-block mb-2")
                        ], width=4, className="text-center"),
                        dbc.Col([
                            html.Img(src=get_image_url(app, 'icea.png'), style={'height': '50px', 'width': 'auto'}, className="mx-auto d-block mb-2")
                        ], width=4, className="text-center"),
                        dbc.Col([
                            html.Img(src=get_image_url(app, 'geocalor.png'), style={'height': '50px', 'width': 'auto'}, className="mx-auto d-block mb-2")
                        ], width=4, className="text-center")
                    ], className="justify-content-center align-items-center mb-2")
                ], style={"background-color": "#f8f9fa", "border-radius": "10px"})
            ], className="mt-3")
        ], width=5),
        dbc.Col([
            html.Label("Cidade:"),
            dcc.Dropdown(
                id="cidade-temp",
                options=[{"label": c, "value": c} for c in cidades] if cidades else [],
                value=cidades[0] if cidades and len(cidades) > 0 else None
            ),
            dcc.Loading(dcc.Graph(id="grafico-temp")),
            dcc.Loading(dcc.Graph(id="grafico-umidade"))
        ], width=7)
    ])
], fluid=True)

@app.callback(
    [Output("grafico-temp", "figure"),
     Output("grafico-umidade", "figure")],
    [Input("cidade-temp", "value"),
     Input("slider-anos", "value")]
)
def update_temp(cidade, anos_selecionados):
    if not cidade or df.empty or not anos_selecionados or len(anos_selecionados) < 2:
        return visualizer.create_temperature_plot(pd.DataFrame(), "", 0, 0), visualizer.create_umidity_plot(pd.DataFrame(), "", 0, 0)
    
    try:
        ano_inicio, ano_fim = anos_selecionados
    except (ValueError, TypeError):
        ano_inicio, ano_fim = 1981, 2023
    
    return (
        visualizer.create_temperature_plot(df, cidade, ano_inicio, ano_fim),
        visualizer.create_umidity_plot(df, cidade, ano_inicio, ano_fim)
    )

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
