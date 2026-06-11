import streamlit as st
import plotly.express as px
from config.database import fetch_data, apply_dynamic_filters
from components.charts import plot_piramide_etaria, plot_raca_cor
from queries.dashboard_queries import get_query_piramide_etaria, get_query_raca_cor

st.title("Perfil Demográfico")
st.markdown("### Análise da População Afetada pelo Zika Vírus")

filtros = st.session_state.get("filtros_globais", {})

df_demo = fetch_data(get_query_piramide_etaria())

if df_demo.empty:
    st.warning("Dados não carregados (vw_piramide_etaria).")
else:
    # A view tem apenas 'faixa' e 'cs_sexo'. O filtro de 'ano' ou 'uf' não terá efeito.
    df_filtrado = apply_dynamic_filters(df_demo, filtros)
    
    if not df_filtrado.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="section-title">Pirâmide Etária</div>', unsafe_allow_html=True)
            fig_piramide = plot_piramide_etaria(df_filtrado)
            st.plotly_chart(fig_piramide, use_container_width=True)
            
        with col2:
            st.markdown('<div class="section-title">Proporção por Sexo</div>', unsafe_allow_html=True)
            df_sexo = df_filtrado.groupby('cs_sexo')['quantidade'].sum().reset_index()
            fig_pie = px.pie(
                df_sexo, 
                values='quantidade', 
                names='cs_sexo',
                color='cs_sexo',
                color_discrete_map={'M': '#4A90E2', 'F': '#E24A84'},
                hole=0.4
            )
            fig_pie.update_layout(margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.markdown("---")
        st.markdown('<div class="section-title">Distribuição Étnico-Racial</div>', unsafe_allow_html=True)
        
        df_raca = fetch_data(get_query_raca_cor())
        if not df_raca.empty:
            fig_raca = plot_raca_cor(df_raca)
            st.plotly_chart(fig_raca, use_container_width=True)
            
        st.markdown("---")
        st.info("💡 **Nota:** Esta página exibe a distribuição por idade, sexo e raça/cor dos casos confirmados. Os filtros de Ano e UF não se aplicam a esta visualização devido ao escopo da consolidação no banco de dados.")
    else:
        st.info("Nenhum dado encontrado para os filtros selecionados.")
