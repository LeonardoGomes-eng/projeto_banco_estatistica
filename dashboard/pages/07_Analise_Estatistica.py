"""
Dashboard de Análise Estatística Avançada
- Sazonalidade e Decomposição Temporal
- Previsão com Prophet
- Tendência por UF
- Agrupamento de Municípios por Perfil Epidemiológico
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

from config.database import fetch_data
from components.statistical_analysis import (
    analyze_seasonality,
    forecast_with_prophet,
    analyze_trend_by_state,
    cluster_municipalities,
    plot_seasonality_decomposition,
    plot_forecast,
    plot_trend_by_state,
    plot_cluster_visualization,
    plot_cluster_radar,
    PROPHET_AVAILABLE
)
from queries.dashboard_queries import get_query_serie_temporal

st.set_page_config(
    page_title="Análise Estatística",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Análise Estatística Avançada - Zika Vírus")
st.markdown("""
    Análise aprofundada com modelos estatísticos avançados:
    **Sazonalidade** | **Previsão (Prophet)** | **Tendência por UF** | **Clustering de Municípios**
""")

# Carregar dados
@st.cache_data(ttl=3600)
def load_analysis_data():
    """Carrega dados para análise estatística"""
    query = """
    SELECT 
        DATE(dt_notific) as data,
        COALESCE(sg_uf, 'Desconhecido') as sg_uf,
        COALESCE(id_municip, 0) as id_municip,
        COUNT(*) as casos,
        SUM(CASE WHEN cs_gestant IN ('1', '2', '3', '4') THEN 1 ELSE 0 END) as gestantes
    FROM notificacoes
    WHERE dt_notific IS NOT NULL
    GROUP BY DATE(dt_notific), sg_uf, id_municip
    ORDER BY data, sg_uf, id_municip
    """
    
    df = fetch_data(query)
    if not df.empty:
        df['data'] = pd.to_datetime(df['data'])
        df['casos'] = df['casos'].fillna(0).astype(int)
        df['gestantes'] = df['gestantes'].fillna(0).astype(int)
    
    return df

# Verificar dependências
if not PROPHET_AVAILABLE:
    st.warning("⚠️ Prophet não está instalado. Instale com: `pip install prophet`")
    st.info("Algumas análises podem estar limitadas.")

# Carregar dados
df_data = load_analysis_data()

if df_data.empty:
    st.error("Nenhum dado disponível para análise.")
    st.stop()

# Barra lateral com filtros
st.sidebar.markdown("### 🔧 Configurações de Análise")
col1, col2 = st.sidebar.columns(2)

with col1:
    n_clusters = st.number_input(
        "Número de Clusters",
        min_value=2,
        max_value=10,
        value=5,
        help="Número de grupos epidemiológicos para K-Means"
    )

with col2:
    forecast_months = st.number_input(
        "Meses de Previsão",
        min_value=1,
        max_value=24,
        value=12,
        help="Meses a prever com Prophet"
    )

# Tabs principais
tabs = st.tabs([
    "🌊 Sazonalidade",
    "🔮 Previsão (Prophet)",
    "📈 Tendência por UF",
    "🗺️ Clustering de Municípios"
])

# ==================== TAB 1: SAZONALIDADE ====================
with tabs[0]:
    st.markdown("### 🌊 Análise de Sazonalidade e Decomposição Temporal")
    
    # Preparar dados agregados por dia
    df_diario = df_data.groupby('data').agg({
        'casos': 'sum',
        'gestantes': 'sum'
    }).reset_index().sort_values('data')
    
    if len(df_diario) >= 24:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            st.metric(
                "Período de Dados",
                f"{len(df_diario)} dias",
                f"{(df_diario['data'].max() - df_diario['data'].min()).days} dias"
            )
        
        # Análise de sazonalidade
        with st.spinner("🔄 Analisando sazonalidade..."):
            seasonality = analyze_seasonality(df_diario, 'casos')
        
        if 'erro' not in seasonality:
            # Métricas de sazonalidade
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Amplitude Sazonal", f"{seasonality['seasonal'].max():.0f} casos")
            with col2:
                st.metric("Período", f"{seasonality['period']} semanas")
            with col3:
                st.metric("Variância Residual", f"{seasonality['residual'].std():.2f}")
            with col4:
                st.metric("Trend Strength", "Forte" if seasonality['trend'].std() > seasonality['residual'].std() else "Fraco")
            
            # Gráfico de decomposição
            fig_decomp = plot_seasonality_decomposition(seasonality)
            if fig_decomp:
                st.plotly_chart(fig_decomp, use_container_width=True)
            
            # Visualizações adicionais
            col1, col2 = st.columns(2)
            
            with col1:
                # Padrão sazonal por semana
                df_seasonal = pd.DataFrame({
                    'semana': range(len(seasonality['seasonal'])),
                    'efeito_sazonal': seasonality['seasonal'].values
                })
                
                # Dividir em ciclos de 52 semanas
                df_seasonal['ciclo'] = df_seasonal['semana'] % 52
                seasonal_pattern = df_seasonal.groupby('ciclo')['efeito_sazonal'].mean()
                
                fig_weekly = go.Figure()
                fig_weekly.add_trace(go.Scatter(
                    x=seasonal_pattern.index,
                    y=seasonal_pattern.values,
                    fill='tozeroy',
                    name='Padrão Sazonal Semanal'
                ))
                
                fig_weekly.update_layout(
                    title='Padrão Sazonal por Semana do Ano',
                    xaxis_title='Semana',
                    yaxis_title='Efeito Sazonal (casos)',
                    height=400
                )
                
                st.plotly_chart(fig_weekly, use_container_width=True)
            
            with col2:
                # Componente trend
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(
                    y=seasonality['trend'],
                    name='Tendência',
                    mode='lines',
                    line=dict(color='red', width=2)
                ))
                
                fig_trend.update_layout(
                    title='Componente de Tendência',
                    xaxis_title='Data',
                    yaxis_title='Casos',
                    height=400
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
            
            # Insights
            st.markdown("#### 📌 Insights de Sazonalidade")
            
            seasonality_months = pd.date_range(start='2020-01-01', periods=52, freq='W')
            peak_week = seasonal_pattern.idxmax()
            low_week = seasonal_pattern.idxmin()
            
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"📍 **Pico de Sazonalidade**: Semana {peak_week} "
                          f"(efeito: +{seasonal_pattern.iloc[peak_week]:.0f} casos)")
            with col2:
                st.info(f"📍 **Vale de Sazonalidade**: Semana {low_week} "
                       f"(efeito: {seasonal_pattern.iloc[low_week]:.0f} casos)")
        
        else:
            st.warning(f"Não foi possível analisar sazonalidade: {seasonality['erro']}")
    
    else:
        st.warning(f"Dados insuficientes. Necessário mínimo 24 dias, disponível: {len(df_diario)} dias")


# ==================== TAB 2: PREVISÃO COM PROPHET ====================
with tabs[1]:
    st.markdown("### 🔮 Previsão de Casos com Prophet")
    
    df_diario = df_data.groupby('data').agg({
        'casos': 'sum'
    }).reset_index().sort_values('data')
    
    if PROPHET_AVAILABLE:
        if len(df_diario) >= 10:
            with st.spinner("⏳ Gerando previsões com Prophet..."):
                forecast_result = forecast_with_prophet(df_diario, periods=forecast_months * 30)
            
            if 'erro' not in forecast_result:
                # Métricas da previsão
                forecast_df = forecast_result['forecast']
                historical_df = forecast_result['dados_historicos']
                
                # Última data histórica
                last_date = historical_df['ds'].max()
                future_forecast = forecast_df[forecast_df['ds'] > last_date]
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Caso Médio (Próx. 30d)",
                        f"{future_forecast.head(30)['yhat'].mean():.0f}",
                        "casos/dia"
                    )
                
                with col2:
                    st.metric(
                        "Caso Máximo (Próx. 90d)",
                        f"{future_forecast.head(90)['yhat'].max():.0f}",
                        "casos/dia"
                    )
                
                with col3:
                    st.metric(
                        "Tendência Geral",
                        "📈 Crescente" if future_forecast['yhat'].mean() > historical_df['y'].mean() else "📉 Decrescente"
                    )
                
                with col4:
                    st.metric(
                        "Confiabilidade",
                        f"{(1 - (future_forecast['yhat_upper'] - future_forecast['yhat_lower']).mean() / future_forecast['yhat'].mean()) * 100:.1f}%"
                    )
                
                # Gráfico principal de previsão
                fig_forecast = plot_forecast(forecast_result, df_diario)
                if fig_forecast:
                    st.plotly_chart(fig_forecast, use_container_width=True)
                
                # Componentes sazonais do Prophet
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Decomposição Temporal (Prophet)")
                    components = forecast_result['componentes']
                    st.pyplot(components, use_container_width=True)
                
                with col2:
                    st.markdown("#### 📊 Estatísticas da Previsão")
                    
                    stats_data = {
                        'Métrica': [
                            'Média Histórica',
                            'Desvio Padrão',
                            'Previsão Média (30d)',
                            'Intervalo de Confiança',
                            'Mudança Esperada'
                        ],
                        'Valor': [
                            f"{historical_df['y'].mean():.2f}",
                            f"{historical_df['y'].std():.2f}",
                            f"{future_forecast.head(30)['yhat'].mean():.2f}",
                            f"[{future_forecast.head(30)['yhat_lower'].mean():.0f} - {future_forecast.head(30)['yhat_upper'].mean():.0f}]",
                            f"{((future_forecast.head(30)['yhat'].mean() / historical_df['y'].mean() - 1) * 100):.1f}%"
                        ]
                    }
                    
                    st.dataframe(
                        pd.DataFrame(stats_data),
                        use_container_width=True,
                        hide_index=True
                    )
                
                # Tabela de previsão detalhada
                st.markdown("#### 📋 Previsão Detalhada (Próximos 90 Dias)")
                
                forecast_display = future_forecast.head(90)[[
                    'ds', 'yhat', 'yhat_lower', 'yhat_upper'
                ]].copy()
                
                forecast_display.columns = ['Data', 'Previsão', 'Limite Inferior', 'Limite Superior']
                forecast_display['Data'] = forecast_display['Data'].dt.strftime('%d/%m/%Y')
                forecast_display['Previsão'] = forecast_display['Previsão'].round(0).astype(int)
                forecast_display['Limite Inferior'] = forecast_display['Limite Inferior'].round(0).astype(int)
                forecast_display['Limite Superior'] = forecast_display['Limite Superior'].round(0).astype(int)
                
                st.dataframe(
                    forecast_display.head(30),
                    use_container_width=True,
                    hide_index=True
                )
            
            else:
                st.error(f"Erro na previsão: {forecast_result['erro']}")
        
        else:
            st.warning(f"Dados insuficientes para previsão. Necessário 10+ dias, disponível: {len(df_diario)}")
    
    else:
        st.error("Prophet não está disponível. Instale com: `pip install prophet`")


# ==================== TAB 3: TENDÊNCIA POR UF ====================
with tabs[2]:
    st.markdown("### 📈 Análise de Tendência por Unidade Federativa")
    
    with st.spinner("🔄 Calculando tendências..."):
        df_trend = analyze_trend_by_state(df_data)
    
    if not df_trend.empty:
        # Seletor de ordenação
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sort_by = st.selectbox(
                "Ordenar por:",
                ["Total de Casos", "Tendência (30d)", "Média Móvel (7d)"],
                key="sort_trend"
            )
        
        with col2:
            show_top = st.slider("Mostrar Estados", 1, len(df_trend), 10)
        
        # Ordenar e filtrar
        if sort_by == "Total de Casos":
            df_trend_sorted = df_trend.nlargest(show_top, 'total_casos')
        elif sort_by == "Tendência (30d)":
            df_trend_sorted = df_trend.nlargest(show_top, 'tendencia_30d')
        else:
            df_trend_sorted = df_trend.nlargest(show_top, 'media_movel_7d')
        
        # Gráficos
        col1, col2 = st.columns(2)
        
        with col1:
            fig_casos = plot_trend_by_state(df_trend_sorted)
            st.plotly_chart(fig_casos, use_container_width=True)
        
        with col2:
            # Gráfico de tendência
            fig_tendencia = px.bar(
                df_trend_sorted.sort_values('tendencia_30d'),
                x='tendencia_30d',
                y='sg_uf',
                orientation='h',
                color='tendencia_30d',
                color_continuous_scale=['red', 'yellow', 'green'],
                title='Tendência de Casos (últimos 30 dias)',
                labels={'sg_uf': 'Estado', 'tendencia_30d': 'Variação (%)'},
                height=500
            )
            
            fig_tendencia.update_layout(
                showlegend=False,
                hovermode='y unified'
            )
            
            st.plotly_chart(fig_tendencia, use_container_width=True)
        
        # Tabela detalhada
        st.markdown("#### 📊 Detalhes por Estado")
        
        display_df = df_trend.copy()
        display_df['Tendência'] = display_df['tendencia_30d'].apply(
            lambda x: f"📈 +{x:.1f}%" if x > 0 else f"📉 {x:.1f}%"
        )
        display_df['Risco'] = display_df['tendencia_30d'].apply(
            lambda x: "🔴 Crescente" if x > 10 else "🟡 Estável" if x > -10 else "🟢 Decrescente"
        )
        
        display_df_view = display_df[[
            'sg_uf', 'total_casos', 'media_movel_7d', 'Tendência', 'Risco'
        ]].copy()
        
        display_df_view.columns = [
            'Estado', 'Total Casos', 'Média Móvel (7d)', 'Tendência', 'Classificação'
        ]
        
        display_df_view['Total Casos'] = display_df_view['Total Casos'].astype(int)
        display_df_view['Média Móvel (7d)'] = display_df_view['Média Móvel (7d)'].round(2)
        
        st.dataframe(
            display_df_view.sort_values('Total Casos', ascending=False),
            use_container_width=True,
            hide_index=True
        )
        
        # Insights
        st.markdown("#### 📌 Insights Principais")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            top_uf = df_trend.iloc[0]
            st.success(f"**🔴 Maior Incidência**: {top_uf['sg_uf']}\n{top_uf['total_casos']:.0f} casos")
        
        with col2:
            crescente = df_trend[df_trend['tendencia_30d'] > 10]
            st.warning(f"**📈 Tendência Crescente**: {len(crescente)} estados")
        
        with col3:
            decrescente = df_trend[df_trend['tendencia_30d'] < -10]
            st.info(f"**📉 Tendência Decrescente**: {len(decrescente)} estados")
    
    else:
        st.error("Não foi possível calcular tendências.")


# ==================== TAB 4: CLUSTERING DE MUNICÍPIOS ====================
with tabs[3]:
    st.markdown("### 🗺️ Agrupamento de Municípios por Perfil Epidemiológico")
    
    with st.spinner("🔄 Executando K-Means clustering..."):
        cluster_result = cluster_municipalities(df_data, n_clusters=n_clusters)
    
    if 'erro' not in cluster_result:
        df_municipios = cluster_result['municipios']
        cluster_profiles = cluster_result['cluster_profiles']
        
        # Estatísticas gerais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Municípios Analisados", len(df_municipios))
        with col2:
            st.metric("Clusters Identificados", n_clusters)
        with col3:
            st.metric("Variância Explicada (PCA)", f"{cluster_result['pca_variance'].sum()*100:.1f}%")
        with col4:
            st.metric("Municípios em Risco Crítico", len(df_municipios[df_municipios['cluster'].isin(
                cluster_profiles[cluster_profiles['risco'] == '🔴 Crítico']['cluster'].values
            )]))
        
        # Visualizações
        col1, col2 = st.columns([1.2, 1])
        
        with col1:
            # Gráfico de clustering em 2D
            fig_cluster = plot_cluster_visualization(cluster_result)
            if fig_cluster:
                st.plotly_chart(fig_cluster, use_container_width=True)
        
        with col2:
            # Gráfico radar dos perfis
            fig_radar = plot_cluster_radar(cluster_profiles)
            if fig_radar:
                st.plotly_chart(fig_radar, use_container_width=True)
        
        # Características dos clusters
        st.markdown("#### 🎯 Perfil dos Clusters")
        
        profile_display = cluster_profiles.copy()
        profile_display.columns = [
            'Cluster', 'Nº Municípios', 'Média Casos', 'Média Incidência (casos/dia)', 'Prop. Gestantes (%)', 'Nível de Risco'
        ]
        profile_display['Nº Municípios'] = profile_display['Nº Municípios'].astype(int)
        profile_display['Média Casos'] = profile_display['Média Casos'].round(0).astype(int)
        profile_display['Média Incidência (casos/dia)'] = profile_display['Média Incidência (casos/dia)'].round(2)
        profile_display['Prop. Gestantes (%)'] = (profile_display['Prop. Gestantes (%)'] * 100).round(1)
        
        st.dataframe(
            profile_display.sort_values('Cluster'),
            use_container_width=True,
            hide_index=True
        )
        
        # Seletor de cluster para detalhes
        st.markdown("#### 📋 Municípios por Cluster")
        
        selected_cluster = st.selectbox(
            "Selecione um cluster para ver os municípios:",
            options=sorted(df_municipios['cluster'].unique()),
            format_func=lambda x: f"Cluster {x} - {cluster_profiles[cluster_profiles['cluster']==x]['risco'].values[0]}"
        )
        
        cluster_mun = df_municipios[df_municipios['cluster'] == selected_cluster].sort_values(
            'total_casos', ascending=False
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.metric("Municípios neste Cluster", len(cluster_mun))
        with col2:
            profile_sel = cluster_profiles[cluster_profiles['cluster'] == selected_cluster].iloc[0]
            st.metric("Nível de Risco", profile_sel['risco'])
        
        # Tabela de municípios
        mun_display = cluster_mun[[
            'id_municip', 'total_casos', 'incidencia_diaria_media', 'proporcao_gestantes'
        ]].head(20).copy()
        
        mun_display.columns = [
            'ID Município', 'Total de Casos', 'Incidência (casos/dia)', 'Proporção Gestantes'
        ]
        
        mun_display['Total de Casos'] = mun_display['Total de Casos'].astype(int)
        mun_display['Incidência (casos/dia)'] = mun_display['Incidência (casos/dia)'].round(3)
        mun_display['Proporção Gestantes'] = (mun_display['Proporção Gestantes'] * 100).round(1)
        
        st.dataframe(
            mun_display,
            use_container_width=True,
            hide_index=True
        )
        
        if len(cluster_mun) > 20:
            st.info(f"📊 Mostrando top 20 de {len(cluster_mun)} municípios")
        
        # Insights por cluster
        st.markdown("#### 📌 Recomendações por Cluster")
        
        for cluster_id in sorted(df_municipios['cluster'].unique()):
            profile = cluster_profiles[cluster_profiles['cluster'] == cluster_id].iloc[0]
            n_mun = len(df_municipios[df_municipios['cluster'] == cluster_id])
            
            with st.expander(f"**{profile['risco']} - Cluster {cluster_id}** ({n_mun} municípios)"):
                if profile['risco'] == '🔴 Crítico':
                    st.error("""
                    ⚠️ **Ações Recomendadas:**
                    - Intensificar vigilância epidemiológica
                    - Aumentar frequência de coleta de dados
                    - Implementar medidas de controle vetorial reforçadas
                    - Priorizar ações de educação em saúde
                    - Monitorar gestantes com maior frequência
                    """)
                elif profile['risco'] == '🟠 Alto':
                    st.warning("""
                    ⚠️ **Ações Recomendadas:**
                    - Manter vigilância intensiva
                    - Realizar campanhas de prevenção regularmente
                    - Reforçar ações de controle vetorial
                    - Acompanhar tendências de forma contínua
                    """)
                elif profile['risco'] == '🟡 Médio':
                    st.info("""
                    ℹ️ **Ações Recomendadas:**
                    - Manter vigilância regular
                    - Realizar campanhas periódicas de prevenção
                    - Monitorar indicadores principais
                    """)
                else:
                    st.success("""
                    ✅ **Ações Recomendadas:**
                    - Manter vigilância de rotina
                    - Continuar monitorando indicadores
                    - Realizar campanhas educacionais periódicas
                    """)
    
    else:
        st.error(f"Erro ao executar clustering: {cluster_result.get('erro', 'Desconhecido')}")


# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666;">
    📊 Dashboard de Análise Estatística Avançada | Zika Vírus - SINAN<br>
    Última atualização: """ + datetime.now().strftime("%d/%m/%Y %H:%M") + """
    </div>
""", unsafe_allow_html=True)
