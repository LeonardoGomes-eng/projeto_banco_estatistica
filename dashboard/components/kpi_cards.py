import streamlit as st
import pandas as pd

def render_kpi_card(title: str, value: str, icon: str = "", subtitle: str = "", trend: str = ""):
    """
    Renderiza um cartão de KPI com HTML/CSS personalizado para visual premium.
    A estilização real é injetada via config/theme.py.
    """
    
    trend_html = ""
    if trend:
        if "up" in trend.lower() or "+" in trend:
            trend_class = "kpi-up"
        elif "down" in trend.lower() or "-" in trend:
            trend_class = "kpi-down"
        else:
            trend_class = "text_muted"
            
        trend_html = f'<div class="kpi-subtitle {trend_class}">{trend} {subtitle}</div>'
    elif subtitle:
        trend_html = f'<div class="kpi-subtitle text_muted">{subtitle}</div>'

    html_content = f"""
    <div class="kpi-card">
        <div class="kpi-title">{icon} {title}</div>
        <div class="kpi-value">{value}</div>
        {trend_html}
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

def render_visao_executiva_kpis(df_kpi: pd.DataFrame):
    """
    Renderiza os KPIs lendo diretamente da view `vw_kpi_cards`.
    A view possui apenas 1 linha com as colunas: 
    total_notificacoes_gerais, total_casos_confirmados, total_obitos_zika, total_gestantes_em_risco
    """
    if df_kpi.empty:
        st.warning("Sem dados na view vw_kpi_cards.")
        return
        
    row = df_kpi.iloc[0]
    total_notificacoes = row.get('total_notificacoes_gerais', 0)
    total_confirmados = row.get('total_casos_confirmados', 0)
    total_obitos = row.get('total_obitos_zika', 0)
    total_gestantes = row.get('total_gestantes_em_risco', 0)
    
    pct_confirmacao = (total_confirmados / total_notificacoes * 100) if total_notificacoes > 0 else 0
    taxa_mortalidade = (total_obitos / total_confirmados * 100) if total_confirmados > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_kpi_card(
            title="Total de Notificações",
            value=f"{total_notificacoes:,.0f}".replace(",", "."),
            icon="📝"
        )
        
    with col2:
        render_kpi_card(
            title="Casos Confirmados",
            value=f"{total_confirmados:,.0f}".replace(",", "."),
            icon="🦠",
            subtitle=f"{pct_confirmacao:.1f}% das notificações",
            trend="up" if pct_confirmacao > 50 else ""
        )
        
    with col3:
        render_kpi_card(
            title="Óbitos por Zika",
            value=f"{total_obitos:,.0f}".replace(",", "."),
            icon="⚠️",
            subtitle=f"{taxa_mortalidade:.2f}% de letalidade",
            trend="down" if total_obitos > 0 else ""
        )
        
    with col4:
        render_kpi_card(
            title="Gestantes em Risco",
            value=f"{total_gestantes:,.0f}".replace(",", "."),
            icon="🤰",
            subtitle="Confirmadas no 1º, 2º ou 3º tri"
        )
