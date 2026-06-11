import streamlit as st
from config.theme import apply_custom_theme
from components.filters import render_global_filters

# Configuração da Página Principal
st.set_page_config(
    page_title="Zika Vírus - SINAN Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplica Tema Customizado (CSS e Plotly)
apply_custom_theme()

# Renderiza os filtros na barra lateral
st.sidebar.markdown("### 📊 SINAN - Zika (2018-2026)")
if "filtros_globais" not in st.session_state:
    st.session_state.filtros_globais = {}
    
st.session_state.filtros_globais = render_global_filters()

# Configuração da Navegação usando o novo st.navigation (Streamlit >= 1.36)
pages = {
    "Dashboards": [
        st.Page("pages/01_Visao_Executiva.py", title="Visão Executiva", icon="📈"),
        st.Page("pages/02_Distribuicao_Geografica.py", title="Distribuição Geográfica", icon="🗺️"),
        st.Page("pages/03_Perfil_Demografico.py", title="Perfil Demográfico", icon="👥"),
        st.Page("pages/04_Gestantes.py", title="Vigilância de Gestantes", icon="🤰"),
        st.Page("pages/06_Monitoramento_Vigilancia.py", title="Monitoramento da Vigilância", icon="⏳"),
    ],
    "Análise Avançada": [
        st.Page("pages/07_Analise_Estatistica.py", title="Análise Estatística Avançada", icon="📊"),
    ],
    "Administração": [
        st.Page("pages/05_Qualidade_Auditoria.py", title="Qualidade & Auditoria", icon="⚙️"),
    ]
}

pg = st.navigation(pages)
pg.run()
