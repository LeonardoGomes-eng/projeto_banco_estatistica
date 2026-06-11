import streamlit as st
import plotly.io as pio

# Definições de Cores Premium (Paleta)
COLORS = {
    "primary": "#00C4B4",    # Teal vibrante
    "secondary": "#FF6B6B",  # Coral / Alerta de Mortalidade
    "background": "#0E1117", # Fundo escuro padrão Streamlit
    "card_bg": "#1E212A",    # Fundo dos cards (Glass/Dark)
    "text": "#FAFAFA",
    "text_muted": "#888888",
    "border": "#2E323A",
    "highlight": "#FFD166"   # Destaque
}

def apply_custom_theme():
    """Aplica injeção de CSS customizado para os KPI Cards e melhora o layout."""
    
    # Configura o Plotly para usar o template escuro com cores customizadas
    pio.templates.default = "plotly_dark"
    
    custom_css = f"""
    <style>
    /* Oculta os botões padrão do Streamlit (opcional, deixa mais limpo) */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Ajuste de padding do block container */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }}
    
    /* Estilo dos KPI Cards Premium */
    .kpi-card {{
        background-color: {COLORS['card_bg']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        height: 100%;
        margin-bottom: 1rem;
    }}
    
    .kpi-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,200,180,0.15);
        border-color: {COLORS['primary']};
    }}
    
    .kpi-title {{
        color: {COLORS['text_muted']};
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }}
    
    .kpi-value {{
        color: {COLORS['text']};
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 4px;
        font-family: 'Inter', sans-serif;
    }}
    
    .kpi-subtitle {{
        font-size: 0.85rem;
        font-weight: 500;
    }}
    
    .kpi-up {{
        color: {COLORS['primary']};
    }}
    
    .kpi-down {{
        color: {COLORS['secondary']};
    }}
    
    /* Títulos de seção */
    .section-title {{
        font-family: 'Inter', sans-serif;
        color: {COLORS['primary']};
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid {COLORS['border']};
        padding-bottom: 0.5rem;
    }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
