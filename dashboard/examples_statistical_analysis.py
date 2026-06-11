"""
Exemplos de Uso - Análise Estatística Avançada
Demonstra como usar os módulos de análise independentemente do dashboard
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from components.statistical_analysis import (
    analyze_seasonality,
    forecast_with_prophet,
    analyze_trend_by_state,
    cluster_municipalities,
    plot_seasonality_decomposition,
    plot_forecast,
    plot_trend_by_state,
    plot_cluster_visualization
)
from components.statistical_utils import (
    calculate_growth_rate,
    classify_trend,
    detect_outliers_iqr,
    normalize_series,
    standardize_series
)


def example_1_sazonalidade():
    """Exemplo: Análise de Sazonalidade"""
    print("=" * 60)
    print("EXEMPLO 1: ANÁLISE DE SAZONALIDADE")
    print("=" * 60)
    
    # Criar dados de exemplo
    dates = pd.date_range(start='2018-01-01', periods=1000, freq='D')
    casos = np.array([
        50 + 30 * np.sin(2 * np.pi * (i / 365.25)) + 
        5 * np.sin(2 * np.pi * (i / 7)) +
        np.random.normal(0, 5)
        for i in range(len(dates))
    ]).clip(0)
    
    df = pd.DataFrame({
        'data': dates,
        'casos': casos
    })
    
    # Executar análise
    resultado = analyze_seasonality(df, 'casos')
    
    if 'erro' not in resultado:
        print(f"✓ Sazonalidade analisada com sucesso")
        print(f"  - Período: {resultado['period']} semanas")
        print(f"  - Amplitude Sazonal: {resultado['seasonal'].max():.2f} casos")
        print(f"  - Variância Residual: {resultado['residual'].std():.2f}")
    else:
        print(f"✗ Erro: {resultado['erro']}")


def example_2_previsao():
    """Exemplo: Previsão com Prophet"""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: PREVISÃO COM PROPHET")
    print("=" * 60)
    
    # Criar dados de exemplo
    dates = pd.date_range(start='2022-01-01', periods=365, freq='D')
    casos = np.array([
        100 + 50 * np.sin(2 * np.pi * (i / 365.25)) + 
        np.random.normal(0, 10)
        for i in range(len(dates))
    ]).clip(0)
    
    df = pd.DataFrame({
        'data': dates,
        'casos': casos
    })
    
    # Executar previsão
    resultado = forecast_with_prophet(df, periods=90)
    
    if 'erro' not in resultado:
        print(f"✓ Previsão gerada com sucesso")
        forecast = resultado['forecast']
        future = forecast[forecast['ds'] > df['data'].max()]
        print(f"  - Previsão para os próximos 90 dias")
        print(f"  - Média de casos: {future['yhat'].mean():.2f}")
        print(f"  - Máximo esperado: {future['yhat'].max():.2f}")
        print(f"  - Intervalo de confiança: [{future['yhat_lower'].mean():.2f}, {future['yhat_upper'].mean():.2f}]")
    else:
        print(f"✗ Erro: {resultado['erro']}")


def example_3_tendencia_uf():
    """Exemplo: Análise de Tendência por UF"""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: ANÁLISE DE TENDÊNCIA POR UF")
    print("=" * 60)
    
    # Criar dados de exemplo
    dates = pd.date_range(start='2022-01-01', periods=365, freq='D')
    ufs = ['SP', 'RJ', 'BA', 'AM', 'PE']
    
    records = []
    for uf in ufs:
        base = np.random.randint(10, 100)
        for i, date in enumerate(dates):
            casos = int(base + i * np.random.normal(0.1, 0.5) + 
                       10 * np.sin(2 * np.pi * (i / 52)) + 
                       np.random.normal(0, 5))
            records.append({
                'data': date,
                'sg_uf': uf,
                'casos': max(0, casos)
            })
    
    df = pd.DataFrame(records)
    
    # Executar análise
    resultado = analyze_trend_by_state(df)
    
    if not resultado.empty:
        print(f"✓ Tendências calculadas para {len(resultado)} estados")
        print("\nTop 3 estados por casos:")
        for idx, row in resultado.nlargest(3, 'total_casos').iterrows():
            print(f"  - {row['sg_uf']}: {row['total_casos']:.0f} casos, "
                  f"Tendência: {row['tendencia_30d']:+.1f}%")
    else:
        print("✗ Erro ao calcular tendências")


def example_4_clustering():
    """Exemplo: Clustering de Municípios"""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: AGRUPAMENTO DE MUNICÍPIOS (K-MEANS)")
    print("=" * 60)
    
    # Criar dados de exemplo
    np.random.seed(42)
    n_municipios = 500
    
    records = []
    for mun_id in range(n_municipios):
        n_dias = np.random.randint(30, 365)
        cluster_type = np.random.choice(['alto', 'medio', 'baixo'])
        
        if cluster_type == 'alto':
            base_casos = np.random.randint(100, 500)
            base_gestantes = np.random.randint(20, 80)
        elif cluster_type == 'medio':
            base_casos = np.random.randint(20, 100)
            base_gestantes = np.random.randint(5, 25)
        else:
            base_casos = np.random.randint(1, 20)
            base_gestantes = np.random.randint(0, 5)
        
        for i in range(n_dias):
            records.append({
                'data': pd.Timestamp('2022-01-01') + timedelta(days=i),
                'id_municip': mun_id,
                'casos': max(0, base_casos + np.random.randint(-10, 20)),
                'gestantes': max(0, base_gestantes + np.random.randint(-2, 5))
            })
    
    df = pd.DataFrame(records)
    
    # Executar clustering
    resultado = cluster_municipalities(df, n_clusters=3)
    
    if 'erro' not in resultado:
        print(f"✓ Clustering realizado com sucesso")
        municipios = resultado['municipios']
        profiles = resultado['cluster_profiles']
        
        print(f"  - {len(municipios)} municípios agrupados")
        print(f"  - Variância explicada (PCA): {resultado['pca_variance'].sum()*100:.1f}%")
        print("\nPerfis dos Clusters:")
        
        for _, row in profiles.iterrows():
            print(f"\n  Cluster {int(row['cluster'])} ({row['risco']})")
            print(f"    - Municípios: {int(row['n_municipios'])}")
            print(f"    - Média de casos: {row['media_casos']:.0f}")
            print(f"    - Média de incidência: {row['media_incidencia']:.2f} casos/dia")
            print(f"    - Proporção de gestantes: {row['media_gestantes']*100:.1f}%")
    else:
        print(f"✗ Erro: {resultado.get('erro', 'Desconhecido')}")


def example_5_utilitarios():
    """Exemplo: Funções Utilitárias"""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: FUNÇÕES UTILITÁRIAS")
    print("=" * 60)
    
    # Dados de exemplo
    historical = pd.Series([100, 105, 110, 108, 115, 120])
    current = 125
    
    # Taxa de crescimento
    growth = calculate_growth_rate(current, historical.mean())
    trend = classify_trend(growth)
    
    print(f"✓ Análise de Crescimento")
    print(f"  - Histórico médio: {historical.mean():.2f}")
    print(f"  - Valor atual: {current}")
    print(f"  - Taxa de crescimento: {growth:+.2f}%")
    print(f"  - Classificação: {trend}")
    
    # Detecção de outliers
    series = pd.Series([10, 12, 11, 13, 100, 12, 11])  # 100 é outlier
    outliers = detect_outliers_iqr(series)
    
    print(f"\n✓ Detecção de Outliers")
    print(f"  - Valores: {series.values}")
    print(f"  - Outliers detectados: {outliers.sum()} valores")
    print(f"  - Índices: {np.where(outliers)[0].tolist()}")
    
    # Normalização e padronização
    print(f"\n✓ Normalização e Padronização")
    print(f"  - Série original: {series.values}")
    normalized = normalize_series(series)
    print(f"  - Normalizada [0,1]: {normalized.values}")
    standardized = standardize_series(series)
    print(f"  - Padronizada (z-score): {standardized.values}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " EXEMPLOS DE USO - ANÁLISE ESTATÍSTICA AVANÇADA ".center(58) + "║")
    print("╚" + "=" * 58 + "╝")
    
    try:
        example_1_sazonalidade()
        example_2_previsao()
        example_3_tendencia_uf()
        example_4_clustering()
        example_5_utilitarios()
        
        print("\n" + "=" * 60)
        print("✓ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERRO: {str(e)}\n")
        import traceback
        traceback.print_exc()
