"""
Utilitários para Análise Estatística
Funções auxiliares para formatação, validação e cálculos comuns
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st


def format_number(num: float, decimals: int = 0) -> str:
    """Formata número para visualização"""
    if decimals == 0:
        return f"{int(num):,}".replace(',', '.')
    return f"{num:.{decimals}f}".replace('.', ',')


def calculate_growth_rate(current: float, previous: float) -> float:
    """Calcula taxa de crescimento percentual"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100


def classify_trend(growth_rate: float, threshold_high: float = 10, 
                   threshold_low: float = -10) -> str:
    """Classifica tendência baseada em taxa de crescimento"""
    if growth_rate > threshold_high:
        return "📈 Crescente"
    elif growth_rate < threshold_low:
        return "📉 Decrescente"
    else:
        return "→ Estável"


def get_trend_color(growth_rate: float) -> str:
    """Retorna cor HTML baseada em tendência"""
    if growth_rate > 10:
        return "#FF4444"  # Vermelho
    elif growth_rate > -10:
        return "#FFD700"  # Amarelo
    else:
        return "#90EE90"  # Verde


def calculate_moving_average(series: pd.Series, window: int = 7) -> pd.Series:
    """Calcula média móvel simples"""
    return series.rolling(window=window, min_periods=1).mean()


def calculate_exponential_moving_average(series: pd.Series, span: int = 7) -> pd.Series:
    """Calcula média móvel exponencial"""
    return series.ewm(span=span, adjust=False).mean()


def detect_outliers_iqr(data: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """Detecta outliers usando método IQR (Interquartil Range)"""
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - (multiplier * IQR)
    upper_bound = Q3 + (multiplier * IQR)
    
    return (data < lower_bound) | (data > upper_bound)


def calculate_r_squared(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calcula coeficiente de determinação R²"""
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    
    if ss_tot == 0:
        return 0
    
    return 1 - (ss_res / ss_tot)


def calculate_mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calcula Mean Absolute Error"""
    return np.mean(np.abs(actual - predicted))


def calculate_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Calcula Root Mean Square Error"""
    return np.sqrt(np.mean((actual - predicted) ** 2))


def validate_dataframe_for_analysis(df: pd.DataFrame, required_columns: list) -> tuple:
    """Valida se DataFrame contém colunas necessárias"""
    missing = set(required_columns) - set(df.columns)
    
    if missing:
        return False, f"Colunas faltantes: {', '.join(missing)}"
    
    if df.empty:
        return False, "DataFrame vazio"
    
    return True, "Validação bem-sucedida"


def aggregate_time_series(df: pd.DataFrame, date_col: str, value_col: str, 
                          freq: str = 'D') -> pd.DataFrame:
    """Agrega série temporal para frequência especificada"""
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    df_copy = df_copy.set_index(date_col)
    
    aggregated = df_copy[value_col].resample(freq).sum()
    return aggregated.reset_index().rename(columns={value_col: 'valor'})


def calculate_seasonality_index(series: pd.Series, period: int = 52) -> pd.Series:
    """Calcula índice de sazonalidade (seasonal factor)"""
    if len(series) < period:
        return pd.Series(np.ones(len(series)))
    
    # Média geral
    overall_mean = series.mean()
    
    # Média por período (semanal, mensal, etc)
    seasonal_factors = []
    for i in range(period):
        indices = np.arange(i, len(series), period)
        if len(indices) > 0:
            factor = series.iloc[indices].mean() / overall_mean if overall_mean != 0 else 1
            seasonal_factors.append(factor)
    
    # Repetir para toda série
    n_cycles = (len(series) // period) + 1
    seasonal_index = (seasonal_factors * n_cycles)[:len(series)]
    
    return pd.Series(seasonal_index, index=series.index)


def get_date_range_summary(df: pd.DataFrame, date_col: str) -> dict:
    """Retorna resumo do período coberto pelos dados"""
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    
    return {
        'data_inicio': df_copy[date_col].min(),
        'data_fim': df_copy[date_col].max(),
        'dias_totais': (df_copy[date_col].max() - df_copy[date_col].min()).days,
        'anos_cobertos': (df_copy[date_col].max() - df_copy[date_col].min()).days / 365.25
    }


def normalize_series(series: pd.Series) -> pd.Series:
    """Normaliza série para intervalo [0, 1]"""
    min_val = series.min()
    max_val = series.max()
    
    if min_val == max_val:
        return pd.Series(np.ones(len(series)) * 0.5)
    
    return (series - min_val) / (max_val - min_val)


def standardize_series(series: pd.Series) -> pd.Series:
    """Padroniza série (z-score)"""
    mean = series.mean()
    std = series.std()
    
    if std == 0:
        return pd.Series(np.zeros(len(series)))
    
    return (series - mean) / std


def calculate_correlation_matrix(df: pd.DataFrame, numeric_only: bool = True) -> pd.DataFrame:
    """Calcula matriz de correlação"""
    if numeric_only:
        return df.select_dtypes(include=[np.number]).corr()
    return df.corr()


def find_peaks(series: pd.Series, height_threshold: float = None) -> list:
    """Encontra picos em uma série temporal"""
    peaks = []
    
    for i in range(1, len(series) - 1):
        if series.iloc[i] > series.iloc[i-1] and series.iloc[i] > series.iloc[i+1]:
            if height_threshold is None or series.iloc[i] > height_threshold:
                peaks.append(i)
    
    return peaks


def find_valleys(series: pd.Series, height_threshold: float = None) -> list:
    """Encontra vales em uma série temporal"""
    valleys = []
    
    for i in range(1, len(series) - 1):
        if series.iloc[i] < series.iloc[i-1] and series.iloc[i] < series.iloc[i+1]:
            if height_threshold is None or series.iloc[i] < height_threshold:
                valleys.append(i)
    
    return valleys


def calculate_volatility(returns: pd.Series, window: int = 30) -> float:
    """Calcula volatilidade (desvio padrão dos retornos)"""
    return returns.rolling(window=window).std().mean()


def format_forecast_table(forecast_df: pd.DataFrame, columns_to_show: list = None) -> pd.DataFrame:
    """Formata DataFrame de previsão para exibição"""
    if columns_to_show is None:
        columns_to_show = ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
    
    display_df = forecast_df[columns_to_show].copy()
    
    # Formatar datas
    if 'ds' in display_df.columns:
        display_df['ds'] = display_df['ds'].dt.strftime('%d/%m/%Y')
    
    # Formatar valores
    for col in ['yhat', 'yhat_lower', 'yhat_upper']:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(0).astype(int)
    
    return display_df


def create_summary_statistics(df: pd.DataFrame, value_col: str, group_cols: list = None) -> dict:
    """Cria resumo estatístico dos dados"""
    if group_cols:
        grouped = df.groupby(group_cols)[value_col]
    else:
        grouped = df[value_col]
    
    return {
        'media': grouped.mean(),
        'mediana': grouped.median(),
        'desvio_padrao': grouped.std(),
        'minimo': grouped.min(),
        'maximo': grouped.max(),
        'q25': grouped.quantile(0.25),
        'q75': grouped.quantile(0.75),
        'iqr': grouped.quantile(0.75) - grouped.quantile(0.25)
    }
