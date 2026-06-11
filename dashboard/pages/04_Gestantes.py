import streamlit as st
import plotly.express as px
from config.database import fetch_data, apply_dynamic_filters
from components.charts import plot_casos_gestantes_trimestre
from components.kpi_cards import render_kpi_card
from queries.dashboard_queries import get_query_vigilancia_gestantes

st.title("Vigilância de Gestantes")
st.markdown("### Monitoramento Especial de Casos em Gestantes")

filtros = st.session_state.get("filtros_globais", {})

df_gestantes = fetch_data(get_query_vigilancia_gestantes())

if df_gestantes.empty:
    st.warning("Dados não carregados (vw_vigilancia_gestantes).")
else:
    df_filtrado = apply_dynamic_filters(df_gestantes, filtros)
    
    if not df_filtrado.empty:
        st.markdown('<div class="section-title">Indicadores de Risco (Gestantes Confirmadas)</div>', unsafe_allow_html=True)
        
        total_gestantes = df_filtrado['gestantes_confirmadas'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_kpi_card("Gestantes Confirmadas", f"{total_gestantes:,.0f}".replace(",", "."), "🤰")
        with col2:
            pass # Espaço vazio para centralizar ou adicionar futuras métricas
        with col3:
            pass
            
        st.markdown("---")
        
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.markdown('<div class="section-title">Por Trimestre Gestacional</div>', unsafe_allow_html=True)
            fig_trimestre = plot_casos_gestantes_trimestre(df_filtrado)
            st.plotly_chart(fig_trimestre, use_container_width=True)
            
        with col_graf2:
            st.markdown('<div class="section-title">Evolução Histórica em Gestantes</div>', unsafe_allow_html=True)
            df_ano = df_filtrado.groupby('ano')['gestantes_confirmadas'].sum().reset_index()
            fig_linha = px.line(df_ano, x='ano', y='gestantes_confirmadas', markers=True)
            fig_linha.update_traces(line=dict(color='#FF6B6B', width=3))
            st.plotly_chart(fig_linha, use_container_width=True)
                
        st.markdown('<div class="section-title">Ranking de UFs - Gestantes Notificadas</div>', unsafe_allow_html=True)
        df_uf_gest = df_filtrado.groupby('uf')['gestantes_confirmadas'].sum().reset_index().sort_values('gestantes_confirmadas', ascending=False).head(10)
        fig_bar_gest = px.bar(df_uf_gest, x='uf', y='gestantes_confirmadas', color='gestantes_confirmadas', color_continuous_scale="Reds")
        st.plotly_chart(fig_bar_gest, use_container_width=True)
    else:
        st.info("Não há dados de gestantes para os filtros selecionados.")
