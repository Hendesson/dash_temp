"""
Visualizações para dashboard de temperaturas.
Versão simplificada - apenas gráficos de temperatura e umidade.
"""
import plotly.graph_objs as go
from typing import Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Visualizer:
    def __init__(self):
        pass

    def create_temperature_plot(
        self,
        df: pd.DataFrame,
        cidade: str,
        ano_inicio: int,
        ano_fim: int
    ) -> go.Figure:
        """Cria o gráfico de temperaturas."""
        if df.empty:
            return go.Figure()
        
        dff = df[
            (df["cidade"] == cidade) & 
            (df["year"] >= ano_inicio) & 
            (df["year"] <= ano_fim)
        ]
        
        if dff.empty:
            return go.Figure()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["tempMax"],
            name="Máxima",
            line=dict(color="red")
        ))
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["tempMed"],
            name="Média",
            line=dict(color="yellow")
        ))
        fig.add_trace(go.Scatter(
            x=dff["index"],
            y=dff["tempMin"],
            name="Mínima",
            line=dict(color="blue")
        ))
        
        fig.update_layout(
            title=f"Temperaturas em {cidade} ({ano_inicio}-{ano_fim})",
            xaxis_title="Data",
            yaxis_title="Temperatura (°C)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=12),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    def create_umidity_plot(
        self,
        df: pd.DataFrame,
        cidade: str,
        ano_inicio: int,
        ano_fim: int
    ) -> go.Figure:
        """Cria o gráfico de umidades médias mensais."""
        if df.empty:
            return go.Figure()
        
        dff = df[
            (df["cidade"] == cidade) & 
            (df["year"] >= ano_inicio) & 
            (df["year"] <= ano_fim)
        ]
        
        if dff.empty:
            return go.Figure()
        
        # Tenta usar HumidadeMed primeiro, depois umidade
        umidade_col = None
        if "HumidadeMed" in dff.columns:
            umidade_col = "HumidadeMed"
        elif "umidade" in dff.columns:
            umidade_col = "umidade"
        else:
            return go.Figure()
        
        # Calcula a média mensal de umidade
        monthly_umidity = dff.groupby(dff["index"].dt.month)[umidade_col].mean().reset_index()
        monthly_umidity["mes"] = monthly_umidity["index"].map({
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_umidity["mes"],
            y=monthly_umidity[umidade_col],
            name="Umidade Média",
            line=dict(color="rgb(0, 128, 255)")
        ))
        
        fig.update_layout(
            title=f"Umidade Média Mensal em {cidade} ({ano_inicio}-{ano_fim})",
            xaxis_title="Mês",
            yaxis_title="Umidade Relativa (%)",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(size=12),
            hovermode="x unified",
            xaxis=dict(
                categoryorder="array",
                categoryarray=[
                    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
                ]
            )
        )
        return fig
