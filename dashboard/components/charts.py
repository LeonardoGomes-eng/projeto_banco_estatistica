import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config.theme import COLORS

def plot_curva_epidemiologica(df: pd.DataFrame):
    """
    Gera a curva epidemiológica (série temporal anual).
    Espera as colunas: ano, total_casos_confirmados
    """
    if df.empty or 'ano' not in df.columns:
        return go.Figure()
        
    # Agrupa apenas por ano, pois a semana está nula na maioria dos registros
    df_agg = df.groupby('ano')['total_casos_confirmados'].sum().reset_index()
    
    # Ordena cronologicamente
    df_agg = df_agg.sort_values(by='ano')
    
    fig = px.line(
        df_agg, 
        x='ano', 
        y='total_casos_confirmados',
        title="Curva Epidemiológica do Zika Vírus (Casos Confirmados)",
        labels={'ano': 'Ano de Notificação', 'total_casos_confirmados': 'Total Casos Confirmados'},
        markers=True
    )
    
    fig.update_xaxes(type='category')
    fig.update_traces(line=dict(color=COLORS['primary'], width=3), marker=dict(size=8))
    fig.update_layout(
        hovermode="x unified",
        xaxis_tickangle=0,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_piramide_etaria(df: pd.DataFrame):
    """
    Gera o gráfico da pirâmide etária.
    Espera colunas: faixa, cs_sexo, quantidade
    """
    if df.empty or 'faixa' not in df.columns or 'cs_sexo' not in df.columns:
        return go.Figure()
        
    df_agg = df.groupby(['faixa', 'cs_sexo'])['quantidade'].sum().reset_index()
    
    df_masc = df_agg[df_agg['cs_sexo'] == 'M']
    df_fem = df_agg[df_agg['cs_sexo'] == 'F']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=df_masc['faixa'],
        x=-df_masc['quantidade'], # Valores negativos para ir para a esquerda
        name='Masculino',
        orientation='h',
        marker=dict(color='#4A90E2')
    ))
    
    fig.add_trace(go.Bar(
        y=df_fem['faixa'],
        x=df_fem['quantidade'], # Valores positivos para a direita
        name='Feminino',
        orientation='h',
        marker=dict(color='#E24A84')
    ))
    
    fig.update_layout(
        title="Distribuição Demográfica (Pirâmide Etária)",
        barmode='overlay',
        xaxis=dict(
            title="Quantidade de Casos",
            tickvals=[-10000, -5000, 0, 5000, 10000],
            ticktext=['10k', '5k', '0', '5k', '10k']
        ),
        yaxis=dict(title="Faixa Etária"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_casos_uf_bar(df: pd.DataFrame):
    """
    Gera ranking de UFs.
    Espera colunas: ano, uf, total_casos
    """
    if df.empty or 'uf' not in df.columns:
        return go.Figure()
        
    df_agg = df.groupby('uf')['total_casos'].sum().reset_index().sort_values('total_casos', ascending=True)
    
    fig = px.bar(
        df_agg,
        x='total_casos',
        y='uf',
        orientation='h',
        title="Ranking de Casos por Estado",
        labels={'total_casos': 'Total de Casos Confirmados', 'uf': 'Estado'},
        color='total_casos',
        color_continuous_scale='Teal'
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig
    
def plot_casos_gestantes_trimestre(df: pd.DataFrame):
    """
    Gera gráfico de gestantes.
    Espera colunas: ano, uf, trimestre_gestacional, gestantes_confirmadas
    """
    if df.empty or 'trimestre_gestacional' not in df.columns:
        return go.Figure()
        
    df_agg = df.groupby('trimestre_gestacional')['gestantes_confirmadas'].sum().reset_index()
    
    fig = px.pie(
        df_agg, 
        values='gestantes_confirmadas', 
        names='trimestre_gestacional',
        title="Distribuição por Trimestre Gestacional",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Teal
    )
    return fig

def plot_evolucao_casos(df: pd.DataFrame):
    """
    Gera gráfico de desfecho dos casos (Cura vs Óbito).
    Espera colunas: tipo_evolucao, total_casos
    """
    if df.empty or 'tipo_evolucao' not in df.columns:
        return go.Figure()
        
    df_agg = df.groupby('tipo_evolucao')['total_casos'].sum().reset_index()
    
    # Cores personalizadas: Cura (Teal), Óbito Zika (Coral), Outros (Cinza)
    color_map = {
        'Cura': COLORS['primary'],
        'Óbito pelo agravo': COLORS['secondary'],
        'Óbito por outras causas': '#FFB347',
        'Ignorado': '#888888',
        'Em Branco / Sem Informação': '#555555'
    }
    
    fig = px.pie(
        df_agg, 
        values='total_casos', 
        names='tipo_evolucao',
        title="Desfecho Clínico (Evolução dos Casos)",
        hole=0.5,
        color='tipo_evolucao',
        color_discrete_map=color_map
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def plot_raca_cor(df: pd.DataFrame):
    """
    Gera gráfico de barras horizontais para Raça/Cor.
    Espera colunas: raca_cor, total_casos
    """
    if df.empty or 'raca_cor' not in df.columns:
        return go.Figure()
        
    df_agg = df.groupby('raca_cor')['total_casos'].sum().reset_index().sort_values('total_casos', ascending=True)
    
    fig = px.bar(
        df_agg,
        x='total_casos',
        y='raca_cor',
        orientation='h',
        title="Distribuição Étnico-Racial (Casos Confirmados)",
        labels={'total_casos': 'Total de Casos Confirmados', 'raca_cor': 'Raça / Cor'},
        color='total_casos',
        color_continuous_scale='Purples'
    )
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    return fig

def plot_tempo_notificacao(df: pd.DataFrame):
    """
    Gera gráfico de linha para o tempo médio de notificação ao longo dos anos.
    Espera colunas: ano, media_dias_notificacao
    """
    if df.empty or 'ano' not in df.columns:
        return go.Figure()
        
    df_agg = df.groupby('ano')['media_dias_notificacao'].mean().reset_index()
    df_agg = df_agg.sort_values(by='ano')
    
    fig = px.line(
        df_agg, 
        x='ano', 
        y='media_dias_notificacao',
        title="Atraso Médio da Vigilância (Sintomas vs Notificação)",
        labels={'ano': 'Ano', 'media_dias_notificacao': 'Média de Dias (Atraso)'},
        markers=True
    )
    
    fig.update_xaxes(type='category')
    fig.update_traces(line=dict(color='#FFD166', width=4), marker=dict(size=10, symbol='diamond'))
    fig.update_layout(
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    # Adicionar uma linha de referência (meta ideal, ex: 7 dias)
    fig.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Meta Ideal (7 dias)")
    return fig
