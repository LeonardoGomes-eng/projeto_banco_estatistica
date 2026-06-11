# 📊 Análise Estatística Avançada - Guia de Implementação

## 🎯 Funcionalidades Implementadas

Este módulo fornece análises estatísticas avançadas para o dashboard de vigilância epidemiológica do Zika Vírus.

### 1. **🌊 Sazonalidade e Decomposição Temporal**
- **O que faz**: Decompõe a série temporal em componentes de tendência, sazonalidade e resíduos
- **Método**: STL (Seasonal and Trend decomposition using Loess)
- **Métricas**: 
  - Amplitude sazonal (máxima variação sazonal)
  - Período sazonal (52 semanas/ano)
  - Variância residual
  - Força da tendência
- **Visualizações**:
  - Série original + tendência
  - Padrão sazonal por semana do ano
  - Componente de tendência isolado

### 2. **🔮 Previsão com Prophet**
- **O que faz**: Realiza previsão de casos para os próximos 12-24 meses
- **Modelo**: Facebook Prophet
- **Recursos**:
  - Tendência de crescimento
  - Sazonalidade semanal e anual
  - Intervalo de confiança (95%)
  - Detecção automática de mudanças estruturais (changepoints)
- **Métricas**:
  - Caso médio previsto
  - Caso máximo esperado
  - Tendência geral (crescente/decrescente)
  - Confiabilidade da previsão
- **Visualizações**:
  - Série histórica + previsão com intervalo
  - Decomposição de tendência e sazonalidade
  - Tabela detalhada de previsões (90 dias)

### 3. **📈 Análise de Tendência por Unidade Federativa**
- **O que faz**: Analisa a dinâmica de casos em cada estado
- **Indicadores Calculados**:
  - Total de casos históricos
  - Média móvel de 7 dias
  - Variação percentual dos últimos 30 dias
  - Classificação de risco (crescente/estável/decrescente)
- **Visualizações**:
  - Gráfico de barras com total de casos
  - Heatmap de tendências (cores vermelha→amarela→verde)
  - Tabela comparativa por estado

### 4. **🗺️ Agrupamento de Municípios por Perfil Epidemiológico**
- **O que faz**: Agrupa municípios por similaridade de características epidemiológicas
- **Método**: K-Means Clustering com 2-10 clusters
- **Características Utilizadas**:
  - Total de casos notificados
  - Incidência diária média (casos/dia)
  - Proporção de gestantes infectadas
- **Dimensionalidade**: Redução com PCA para visualização 2D
- **Níveis de Risco**:
  - 🔴 **Crítico**: Ação imediata requerida
  - 🟠 **Alto**: Vigilância intensiva necessária
  - 🟡 **Médio**: Acompanhamento regular
  - 🟢 **Baixo**: Vigilância de rotina
- **Visualizações**:
  - Scatter plot com PCA (municípios posicionados)
  - Gráfico radar comparando perfis dos clusters
  - Tabela com detalhes de cada cluster
  - Lista de municípios por cluster

---

## 📦 Dependências Instaladas

```
prophet>=1.1.5          # Previsão de séries temporais
scikit-learn>=1.3.0     # K-Means e preprocessing
scipy>=1.10.0           # Análises estatísticas
statsmodels>=0.14.0     # Decomposição STL
```

---

## 🚀 Como Usar

### Acessar o Dashboard
1. Navegue até a página **"Análise Estatística Avançada"** no menu lateral
2. Escolha uma das 4 abas de análise

### Configurar Análises
- **Número de Clusters**: Ajuste entre 2-10 para agrupamento de municípios (padrão: 5)
- **Meses de Previsão**: Selecione 1-24 meses para previsão (padrão: 12)

### Interpretar Resultados

#### 🌊 Sazonalidade
- **Amplitude Sazonal Alta (>100 casos)**: Existe padrão sazonal importante
- **Período de 52 semanas**: Ciclo anual característico
- **Força da Tendência**: Compara se tendência é mais forte que variações aleatórias

#### 🔮 Previsão
- **Intervalo de Confiança Estreito**: Modelo confiável
- **Intervalo de Confiança Largo**: Maior incerteza (dados irregulares)
- **Comparação Média Histórica vs Previsão**: Indica mudança de padrão

#### 📈 Tendência por UF
- **Variação > +10%**: Estado em crescimento (🔴)
- **Variação entre -10% e +10%**: Estável (🟡)
- **Variação < -10%**: Decrescente (🟢)

#### 🗺️ Clusters
- **Visualização 2D**: Municípios próximos têm perfis similares
- **Gráfico Radar**: Mostra o que diferencia cada cluster
- **Recomendações**: Ações específicas por nível de risco

---

## 🔧 Estrutura Técnica

### Arquivos Criados
```
dashboard/
├── components/
│   └── statistical_analysis.py    # Funções de análise e visualização
├── pages/
│   └── 07_Analise_Estatistica.py  # Interface Streamlit
└── requirements.txt               # Dependências atualizadas
```

### Fluxo de Dados
```
Banco de Dados PostgreSQL
    ↓
fetch_data() (cache 1h)
    ↓
Funções de análise:
  - analyze_seasonality()
  - forecast_with_prophet()
  - analyze_trend_by_state()
  - cluster_municipalities()
    ↓
Visualizações Plotly
    ↓
Dashboard Streamlit
```

### Performance
- **Cache**: Dados são cache por 1 hora para melhor performance
- **Processamento**: Prophet leva ~5-10s dependendo do tamanho dos dados
- **Clustering**: K-Means é rápido para < 10k municípios

---

## ⚠️ Notas Importantes

1. **Dados Necessários**:
   - Sazonalidade: Mínimo 24 dias de dados
   - Prophet: Mínimo 10 dias de dados
   - Clustering: Mínimo 2 municípios

2. **Prophet não Disponível**:
   - Se houver erro de instalação, instale manualmente:
   ```bash
   pip install prophet --no-build-isolation
   ```

3. **Qualidade dos Dados**:
   - Dados com muitos valores faltantes podem afetar análises
   - Prophet funciona melhor com séries sem lacunas

4. **Interpretação**:
   - Sempre considere o contexto epidemiológico
   - Anomalias (campanhas, mudanças comportamentais) afetam previsões
   - Clusters devem ser validados com dados demográficos

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique se todas as dependências estão instaladas
2. Confirme se há dados no banco de dados
3. Verifique a conexão com PostgreSQL

---

**Versão**: 1.0  
**Última Atualização**: Junho 2024  
**Autor**: Sistema SINAN Dashboard
