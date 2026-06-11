import streamlit as st
import plotly.express as px
import json
import urllib.request
from config.database import fetch_data, apply_dynamic_filters
from components.charts import plot_casos_uf_bar
from queries.dashboard_queries import get_query_casos_uf_ano

st.title("Distribuição Geográfica")
st.markdown("### Análise Espacial dos Casos por Unidade Federativa")

filtros = st.session_state.get("filtros_globais", {})

@st.cache_data
def get_geojson_brasil():
    """Baixa o GeoJSON dos estados brasileiros para o mapa choropleth."""
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    try:
        with urllib.request.urlopen(url) as response:
            geojson = json.loads(response.read().decode())
        return geojson
    except Exception as e:
        st.error("Erro ao carregar malha geográfica do Brasil.")
        return None

df_geo = fetch_data(get_query_casos_uf_ano())

if df_geo.empty:
    st.warning("Dados não carregados (vw_casos_uf_ano).")
else:
    df_filtrado = apply_dynamic_filters(df_geo, filtros)
    
    if not df_filtrado.empty:
        # Agrupa casos por UF
        df_uf = df_filtrado.groupby('uf')['total_casos'].sum().reset_index()
        
        geojson = get_geojson_brasil()
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown('<div class="section-title">Mapa de Densidade (Choropleth)</div>', unsafe_allow_html=True)
            if geojson:
                fig_map = px.choropleth(
                    df_uf, 
                    geojson=geojson, 
                    locations='uf', 
                    featureidkey='properties.sigla',
                    color='total_casos',
                    color_continuous_scale="Teal",
                    title="Densidade de Casos Notificados",
                    labels={'total_casos': 'Total de Casos'}
                )
                fig_map.update_geos(fitbounds="locations", visible=False)
                fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0), geo=dict(bgcolor='rgba(0,0,0,0)'))
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("Malha geográfica indisponível.")
                
        with col2:
            st.markdown('<div class="section-title">Ranking de UFs</div>', unsafe_allow_html=True)
            fig_bar = plot_casos_uf_bar(df_filtrado)
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.markdown("---")
        st.markdown('<div class="section-title">Heatmap: Ano vs UF</div>', unsafe_allow_html=True)
        
        heatmap_data = df_filtrado.groupby(['uf', 'ano'])['total_casos'].sum().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='uf', columns='ano', values='total_casos').fillna(0)
        
        fig_heat = px.imshow(
            heatmap_pivot,
            labels=dict(x="Ano", y="Estado", color="Casos Confirmados"),
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            color_continuous_scale="Teal",
            aspect="auto"
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Nenhum dado encontrado para os filtros selecionados.")
