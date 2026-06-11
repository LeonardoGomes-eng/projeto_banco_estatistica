import streamlit as st
from config.database import fetch_data, apply_dynamic_filters
from components.kpi_cards import render_visao_executiva_kpis
from components.charts import plot_curva_epidemiologica, plot_evolucao_casos
from queries.dashboard_queries import get_query_kpi_cards, get_query_serie_temporal, get_query_evolucao_casos

st.title("Visão Executiva")
st.markdown("### Panorama Geral Epidemiológico - Zika Vírus")

filtros = st.session_state.get("filtros_globais", {})

# 1. Carrega e renderiza KPIs (Não sofrem efeito dos filtros dinâmicos pois não possuem dimensão temporal/espacial na view)
df_kpi = fetch_data(get_query_kpi_cards())

st.markdown('<div class="section-title">Indicadores Principais (Histórico Completo)</div>', unsafe_allow_html=True)
if not df_kpi.empty:
    render_visao_executiva_kpis(df_kpi)
else:
    st.warning("Falha ao carregar KPIs.")

# 2. Carrega e renderiza Curva Epidemiológica
st.markdown('<div class="section-title">Evolução Temporal</div>', unsafe_allow_html=True)

df_curva = fetch_data(get_query_serie_temporal())
if not df_curva.empty:
    # Filtra por ano (a view tem a coluna 'ano')
    df_curva_filtrada = apply_dynamic_filters(df_curva, filtros)
    
    col_chart, col_evo = st.columns([2, 1])
    with col_chart:
        fig_curva = plot_curva_epidemiologica(df_curva_filtrada)
        st.plotly_chart(fig_curva, use_container_width=True)
        
    with col_evo:
        df_evo = fetch_data(get_query_evolucao_casos())
        if not df_evo.empty:
            fig_evo = plot_evolucao_casos(df_evo)
            st.plotly_chart(fig_evo, use_container_width=True)
        else:
            st.warning("Sem dados de evolução.")
else:
    st.warning("Falha ao carregar dados da curva epidemiológica.")
    
st.markdown("---")
st.info("💡 **Dica Analítica:** A Curva Epidemiológica mostra a série temporal **semanal** de casos confirmados. O Desfecho Clínico mostra se o sistema de saúde conseguiu confirmar a Cura ou se houve Óbito/Dados em Branco.")
