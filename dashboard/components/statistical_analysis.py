"""
Módulo de Análise Estatística Avançada
- Previsão com Prophet
- Sazonalidade
- Tendência por UF
- Agrupamento de municípios com K-Means
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import warnings

warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    Prophet = None


def analyze_seasonality(df: pd.DataFrame, column: str = 'casos') -> dict:
    """
    Analisa sazonalidade dos dados usando decomposição STL
    """
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        # Preparar série temporal
        ts_data = df.set_index('data').sort_index()
        
        # Se temos menos de 2 ciclos, não podemos fazer decomposição
        if len(ts_data) < 24:
            return {'erro': 'Dados insuficientes para análise de sazonalidade'}
        
        # Decomposição
        decomposition = seasonal_decompose(
            ts_data[column].fillna(ts_data[column].mean()),
            model='additive',
            period=52  # 52 semanas em um ano
        )
        
        return {
            'trend': decomposition.trend,
            'seasonal': decomposition.seasonal,
            'residual': decomposition.resid,
            'original': decomposition.observed,
            'period': 52
        }
    except Exception as e:
        return {'erro': str(e)}


def forecast_with_prophet(df: pd.DataFrame, periods: int = 12) -> dict:
    """
    Realiza previsão de casos usando Prophet
    """
    if not PROPHET_AVAILABLE:
        return {'erro': 'Prophet não está instalado'}
    
    try:
        # Preparar dados para Prophet (colunas: ds, y)
        df_prophet = df[['data', 'casos']].copy()
        df_prophet.columns = ['ds', 'y']
        df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
        df_prophet = df_prophet.sort_values('ds').drop_duplicates('ds')
        
        if len(df_prophet) < 10:
            return {'erro': 'Dados insuficientes para previsão'}
        
        # Criar e ajustar modelo
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
            interval_width=0.95,
            seasonality_mode='additive',
            changepoint_prior_scale=0.05
        )
        
        with st.spinner('🔮 Gerando previsões com Prophet...'):
            model.fit(df_prophet)
        
        # Criar futuro
        future = model.make_future_dataframe(periods=periods, freq='D')
        forecast = model.predict(future)
        
        return {
            'forecast': forecast,
            'model': model,
            'dados_historicos': df_prophet,
            'componentes': model.plot_components(forecast)
        }
    except Exception as e:
        return {'erro': f'Erro ao gerar previsão: {str(e)}'}


def analyze_trend_by_state(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analisa tendência de casos por UF
    Calcula: total casos, média móvel, tendência (crescente/decrescente)
    """
    try:
        df_copy = df.copy()
        df_copy['data'] = pd.to_datetime(df_copy['data'])
        
        # Agrupar por UF e data
        df_uf = df_copy.groupby(['sg_uf', 'data']).agg({
            'casos': 'sum'
        }).reset_index().sort_values('data')
        
        # Calcular média móvel 7 dias
        df_uf['media_movel_7d'] = df_uf.groupby('sg_uf')['casos'].transform(
            lambda x: x.rolling(window=7, min_periods=1).mean()
        )
        
        # Calcular tendência (variação percentual últimos 30 dias vs 30 dias anteriores)
        result = []
        for uf in df_uf['sg_uf'].unique():
            df_uf_state = df_uf[df_uf['sg_uf'] == uf].sort_values('data')
            
            # Últimos 30 dias
            recent = df_uf_state.tail(30)['casos'].sum()
            # 30 dias antes
            previous = df_uf_state.iloc[-60:-30]['casos'].sum() if len(df_uf_state) >= 60 else 1
            
            tendencia = ((recent - previous) / max(previous, 1)) * 100
            
            result.append({
                'sg_uf': uf,
                'total_casos': df_uf_state['casos'].sum(),
                'media_movel_7d': df_uf_state['media_movel_7d'].iloc[-1],
                'tendencia_30d': tendencia,
                'cases_recentes': recent,
                'data_inicio': df_uf_state['data'].min(),
                'data_fim': df_uf_state['data'].max()
            })
        
        return pd.DataFrame(result).sort_values('total_casos', ascending=False)
    
    except Exception as e:
        st.error(f'Erro ao analisar tendência por UF: {str(e)}')
        return pd.DataFrame()


def cluster_municipalities(df: pd.DataFrame, n_clusters: int = 5) -> dict:
    """
    Agrupa municípios por perfil epidemiológico usando K-Means
    Características: incidência, tendência, população afetada, proporção gestantes
    """
    try:
        df_copy = df.copy()
        df_copy['data'] = pd.to_datetime(df_copy['data'])
        
        # Agregar por município
        df_municipios = df_copy.groupby('id_municip').agg({
            'casos': 'sum',
            'gestantes': 'sum',
            'data': ['min', 'max']
        }).reset_index()
        
        df_municipios.columns = ['id_municip', 'total_casos', 'total_gestantes', 'data_inicio', 'data_fim']
        
        # Calcular dias de monitoramento
        df_municipios['dias_monitorados'] = (
            df_municipios['data_fim'] - df_municipios['data_inicio']
        ).dt.days + 1
        
        # Calcular incidência diária média
        df_municipios['incidencia_diaria_media'] = (
            df_municipios['total_casos'] / df_municipios['dias_monitorados'].replace(0, 1)
        )
        
        # Calcular proporção de gestantes
        df_municipios['proporcao_gestantes'] = (
            df_municipios['total_gestantes'] / df_municipios['total_casos'].replace(0, 1)
        )
        
        # Features para clustering
        features_scaling = df_municipios[[
            'total_casos',
            'incidencia_diaria_media',
            'proporcao_gestantes'
        ]].copy()
        
        # Remover linhas com NaN
        mask = ~features_scaling.isna().any(axis=1)
        df_municipios_clean = df_municipios[mask].copy()
        features_scaling = features_scaling[mask].copy()
        
        if len(df_municipios_clean) < n_clusters:
            n_clusters = max(2, len(df_municipios_clean) // 2)
        
        # Padronizar features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features_scaling)
        
        # K-Means
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df_municipios_clean['cluster'] = kmeans.fit_predict(features_scaled)
        
        # PCA para visualização 2D
        pca = PCA(n_components=2)
        pca_features = pca.fit_transform(features_scaled)
        df_municipios_clean['pca_1'] = pca_features[:, 0]
        df_municipios_clean['pca_2'] = pca_features[:, 1]
        
        # Caracterização dos clusters
        cluster_profiles = []
        for cluster_id in range(n_clusters):
            cluster_data = df_municipios_clean[df_municipios_clean['cluster'] == cluster_id]
            cluster_profiles.append({
                'cluster': cluster_id,
                'n_municipios': len(cluster_data),
                'media_casos': cluster_data['total_casos'].mean(),
                'media_incidencia': cluster_data['incidencia_diaria_media'].mean(),
                'media_gestantes': cluster_data['proporcao_gestantes'].mean(),
                'risco': classify_risk_level(
                    cluster_data['total_casos'].mean(),
                    cluster_data['proporcao_gestantes'].mean()
                )
            })
        
        return {
            'municipios': df_municipios_clean,
            'cluster_profiles': pd.DataFrame(cluster_profiles),
            'pca_variance': pca.explained_variance_ratio_,
            'scaler': scaler,
            'kmeans': kmeans,
            'pca': pca
        }
    
    except Exception as e:
        st.error(f'Erro ao realizar clustering: {str(e)}')
        return {'erro': str(e)}


def classify_risk_level(casos_media: float, prop_gestantes: float) -> str:
    """
    Classifica nível de risco baseado em critérios epidemiológicos
    """
    risk_score = (casos_media * 0.6) + (prop_gestantes * 100 * 0.4)
    
    if risk_score > 50:
        return '🔴 Crítico'
    elif risk_score > 20:
        return '🟠 Alto'
    elif risk_score > 10:
        return '🟡 Médio'
    else:
        return '🟢 Baixo'


def plot_seasonality_decomposition(decomp_data: dict) -> go.Figure:
    """
    Visualiza decomposição de sazonalidade
    """
    if 'erro' in decomp_data:
        return None
    
    fig = go.Figure()
    
    # Original
    fig.add_trace(go.Scatter(
        y=decomp_data['original'],
        name='Original',
        mode='lines'
    ))
    
    # Trend
    fig.add_trace(go.Scatter(
        y=decomp_data['trend'],
        name='Tendência',
        mode='lines',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title='Decomposição Temporal - Sazonalidade',
        xaxis_title='Data',
        yaxis_title='Casos',
        hovermode='x unified',
        height=400
    )
    
    return fig


def plot_forecast(forecast_data: dict, original_df: pd.DataFrame) -> go.Figure:
    """
    Visualiza previsão do Prophet com intervalo de confiança
    """
    if 'erro' in forecast_data:
        return None
    
    forecast = forecast_data['forecast']
    historical = forecast_data['dados_historicos']
    
    # Separar histórico e previsão
    historical_dates = historical['ds'].max()
    
    fig = go.Figure()
    
    # Dados históricos
    fig.add_trace(go.Scatter(
        x=historical['ds'],
        y=historical['y'],
        name='Dados Históricos',
        mode='lines',
        line=dict(color='blue')
    ))
    
    # Previsão
    future_forecast = forecast[forecast['ds'] > historical_dates]
    
    fig.add_trace(go.Scatter(
        x=future_forecast['ds'],
        y=future_forecast['yhat'],
        name='Previsão',
        mode='lines',
        line=dict(color='red', dash='dash')
    ))
    
    # Intervalo de confiança
    fig.add_trace(go.Scatter(
        x=future_forecast['ds'].tolist() + future_forecast['ds'].tolist()[::-1],
        y=future_forecast['yhat_upper'].tolist() + future_forecast['yhat_lower'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(255,0,0,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Intervalo de Confiança (95%)',
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        title='Previsão de Casos - Prophet (próximos 12 meses)',
        xaxis_title='Data',
        yaxis_title='Casos',
        hovermode='x unified',
        height=500
    )
    
    return fig


def plot_trend_by_state(df_trend: pd.DataFrame) -> go.Figure:
    """
    Visualiza tendência por UF com cores de risco
    """
    # Definir cores baseado em tendência
    colors = ['🔴 Crescente' if x > 10 else '🟡 Estável' if x > -10 else '🟢 Decrescente' 
              for x in df_trend['tendencia_30d']]
    
    fig = px.bar(
        df_trend.sort_values('total_casos', ascending=True),
        y='sg_uf',
        x='total_casos',
        orientation='h',
        title='Total de Casos por UF (2018-2026)',
        labels={'sg_uf': 'Estado', 'total_casos': 'Total de Casos'},
        height=500
    )
    
    fig.update_layout(
        hovermode='y unified',
        xaxis_title='Total de Casos',
        yaxis_title='Estado'
    )
    
    return fig


def plot_cluster_visualization(cluster_data: dict) -> go.Figure:
    """
    Visualiza clustering de municípios em 2D usando PCA
    """
    if 'erro' in cluster_data:
        return None
    
    df_mun = cluster_data['municipios']
    cluster_profiles = cluster_data['cluster_profiles']
    
    # Cores para clusters
    color_map = {
        '🔴 Crítico': '#FF4444',
        '🟠 Alto': '#FF8C00',
        '🟡 Médio': '#FFD700',
        '🟢 Baixo': '#90EE90'
    }
    
    fig = go.Figure()
    
    for cluster_id in sorted(df_mun['cluster'].unique()):
        cluster_subset = df_mun[df_mun['cluster'] == cluster_id]
        profile = cluster_profiles[cluster_profiles['cluster'] == cluster_id].iloc[0]
        
        fig.add_trace(go.Scatter(
            x=cluster_subset['pca_1'],
            y=cluster_subset['pca_2'],
            mode='markers',
            name=f"Cluster {cluster_id} - {profile['risco']} ({len(cluster_subset)} mun.)",
            marker=dict(
                size=10,
                color=color_map.get(profile['risco'], '#888888'),
                line=dict(width=1, color='white')
            ),
            text=[f"ID: {id_mun}<br>Casos: {casos:.0f}<br>Incidência: {inc:.2f}" 
                  for id_mun, casos, inc in zip(
                      cluster_subset['id_municip'],
                      cluster_subset['total_casos'],
                      cluster_subset['incidencia_diaria_media']
                  )],
            hovertemplate='%{text}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Agrupamento de Municípios por Perfil Epidemiológico (K-Means)',
        xaxis_title=f'PC1 ({cluster_data["pca_variance"][0]:.1%} variância)',
        yaxis_title=f'PC2 ({cluster_data["pca_variance"][1]:.1%} variância)',
        hovermode='closest',
        height=600,
        width=900
    )
    
    return fig


def plot_cluster_radar(cluster_profiles: pd.DataFrame) -> go.Figure:
    """
    Visualiza perfis dos clusters em gráfico radar
    """
    if cluster_profiles.empty:
        return None
    
    # Normalizar valores para escala 0-100 para melhor visualização
    df_radar = cluster_profiles.copy()
    df_radar['media_casos_norm'] = (
        (df_radar['media_casos'] / df_radar['media_casos'].max()) * 100
    )
    df_radar['media_incidencia_norm'] = (
        (df_radar['media_incidencia'] / df_radar['media_incidencia'].max()) * 100
    )
    df_radar['media_gestantes_norm'] = df_radar['media_gestantes'] * 100
    
    fig = go.Figure()
    
    for _, row in df_radar.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[
                row['media_casos_norm'],
                row['media_incidencia_norm'],
                row['media_gestantes_norm'],
                row['n_municipios'] / df_radar['n_municipios'].max() * 100
            ],
            theta=['Casos Totais', 'Incidência Diária', 'Prop. Gestantes', 'Nº Municípios'],
            fill='toself',
            name=f"Cluster {int(row['cluster'])} - {row['risco']}"
        ))
    
    fig.update_layout(
        title='Perfil Epidemiológico dos Clusters',
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        height=600
    )
    
    return fig
