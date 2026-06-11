import streamlit as st
import pandas as pd

def render_global_filters() -> dict:
    """
    Renderiza os filtros na barra lateral.
    Como utilizamos views pré-agregadas, as opções serão fornecidas baseadas no domínio dos dados.
    """
    st.sidebar.title("🔍 Filtros Globais")
    st.sidebar.markdown("Filtre os dados para todas as visualizações (quando a dimensão estiver disponível na análise).")
    
    filters = {}
    
    # Anos baseados no contexto do projeto (2018-2026)
    anos_disponiveis = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    filters['ano'] = st.sidebar.multiselect(
        "📅 Ano",
        options=anos_disponiveis,
        default=anos_disponiveis,
        help="Selecione os anos de notificação"
    )
            
    # Siglas UF
    ufs_disponiveis = [
        "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", 
        "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", 
        "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"
    ]
    filters['uf'] = st.sidebar.multiselect(
        "📍 UF (Estado)",
        options=ufs_disponiveis,
        help="Selecione os estados (deixe em branco para todos)"
    )
            
    # Sexo
    sexos_disponiveis = ['M', 'F']
    filters['sexo'] = st.sidebar.multiselect(
        "👥 Sexo",
        options=sexos_disponiveis,
        help="Selecione o sexo do paciente (M/F)"
    )
            
    st.sidebar.markdown("---")
    st.sidebar.info("📌 Nota: Os filtros afetam apenas os gráficos que possuem a dimensão correspondente na base de dados.")
    
    if st.sidebar.button("🔄 Atualizar / Limpar"):
        st.rerun()
        
    return filters
