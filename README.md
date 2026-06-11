# 🦠 Dashboard Epidemiológico do Zika Vírus (SINAN)

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.36+-FF4B4B?logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql)
![Pandas](https://img.shields.io/badge/Pandas-2.0+-150458?logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?logo=plotly)

Dashboard interativo desenvolvido em **Python + Streamlit** focado na análise epidemiológica de dados do SINAN (Sistema de Informação de Agravos de Notificação) sobre os casos de Zika Vírus no Brasil entre os anos de 2018 e 2026. 

Este projeto conecta-se a um banco de dados **PostgreSQL** contendo mais de 236 mil notificações, e utiliza views analíticas, validações clínicas via Triggers e gerenciamento de permissões nativas do banco para extrair insights valiosos sobre letalidade, disseminação demográfica, territorial e gestão do tempo de vigilância.

---

## 🎯 Funcionalidades e Análises

O painel é estruturado no formato de Business Intelligence (BI) e dividido em 7 módulos:

### 📊 Dashboards
1. **📈 Visão Executiva:** Evolução clínica, letalidade, KPIs globais e série temporal (curva epidemiológica).
2. **🗺️ Distribuição Geográfica:** Mapa Choropleth de densidade, Ranking estadual e Heatmap de "Ano vs UF" para acompanhar o deslocamento do vírus.
3. **👥 Perfil Demográfico:** Análise da população atingida via Pirâmide Etária e cruzamento Étnico-Racial.
4. **🤰 Vigilância de Gestantes:** Monitoramento avançado focado na proteção contra a Síndrome Congênita do Zika Vírus (Microcefalia).
5. **⏳ Monitoramento da Vigilância:** Cálculo do "Atraso da Vigilância" — Tempo médio (em dias) decorrido entre os primeiros sintomas do paciente e a sua notificação no SUS.

### 📊 Análise Avançada
6. **📊 Análise Estatística Avançada:** Análises estatísticas aprofundadas com modelos de machine learning:
   - **🌊 Sazonalidade:** Decomposição temporal (STL) para identificar padrões sazonais e tendências
   - **🔮 Previsão de Casos:** Modelo Prophet para previsão 1-24 meses com intervalo de confiança
   - **📈 Tendência por UF:** Análise de variação percentual e classificação de risco por estado
   - **🗺️ Clustering de Municípios:** K-Means para agrupamento de municípios por perfil epidemiológico

### ⚙️ Administração
7. **⚙️ Qualidade & Auditoria:** Transparência dos dados, exibindo Triggers de auditoria do banco (INSERTs/UPDATEs) e logs de inconsistências clínicas interceptados pelo BD.

---

## 🚀 Como executar o projeto localmente

Siga o passo a passo abaixo para rodar o Dashboard na sua máquina.

### Pré-requisitos
*   [Python 3.10+](https://www.python.org/downloads/) instalado.
*   [PostgreSQL 15+](https://www.postgresql.org/download/) instalado e rodando.
*   `pgAdmin 4` (Opcional, mas recomendado para gestão do banco).

### Queries necessárias para rodar no banco local:
```sql
-- 1.1 Função para decodificar a idade (Transforma o código NU_IDADE_N do SINAN em anos)
CREATE OR REPLACE FUNCTION fn_decodifica_idade_anos(idade_codificada INTEGER)
RETURNS INTEGER AS $$
DECLARE
    unidade INTEGER;
    quantidade INTEGER;
BEGIN
    IF idade_codificada IS NULL THEN 
        RETURN NULL; 
    END IF;
    
    unidade := idade_codificada / 1000;
    quantidade := idade_codificada % 1000;

    IF unidade = 4 THEN 
        RETURN quantidade;       -- Código 4 indica Anos
    ELSIF unidade IN (1, 2, 3) THEN 
        RETURN 0;                -- Códigos 1 (Horas), 2 (Dias), 3 (Meses) representam < 1 ano
    ELSE 
        RETURN NULL;             -- Valores ignorados ou fora do padrão
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;


-- 1.2 Função para detectar duplicatas (Busca casos suspeitos pelo Ano de Nasc., Sexo e Município)
CREATE OR REPLACE FUNCTION fn_detectar_duplicatas(p_ano_nasc INTEGER, p_sexo CHAR, p_municipio INTEGER)
RETURNS TABLE(id_notificacao BIGINT, dt_notificacao DATE, status_classificacao SMALLINT) AS $$
BEGIN
    RETURN QUERY
    SELECT n.id, n.dt_notific, n.classi_fin
    FROM notificacao n
    WHERE n.ano_nasc = p_ano_nasc
      AND n.cs_sexo = p_sexo
      AND n.id_mn_resi = p_municipio;
END;
$$ LANGUAGE plpgsql STABLE;


-- Criação da tabela de auditoria baseada no ERD
CREATE TABLE IF NOT EXISTS auditoria_notificacao (
    audit_id BIGSERIAL PRIMARY KEY,
    operacao CHAR(1), -- 'I' (Insert), 'U' (Update), 'D' (Delete)
    notificacao_id BIGINT,
    usuario VARCHAR(50),
    momento TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dado_anterior JSONB,
    dado_posterior JSONB
);

-- 2.1 Trigger Function para Auditoria (Snapshot JSONB)
CREATE OR REPLACE FUNCTION fn_auditoria_notificacao()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO auditoria_notificacao(operacao, notificacao_id, usuario, dado_posterior)
        VALUES ('I', NEW.id, current_user, to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO auditoria_notificacao(operacao, notificacao_id, usuario, dado_anterior, dado_posterior)
        VALUES ('U', NEW.id, current_user, to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria_notificacao(operacao, notificacao_id, usuario, dado_anterior)
        VALUES ('D', OLD.id, current_user, to_jsonb(OLD));
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Acionador (Trigger) de Auditoria
CREATE TRIGGER trg_auditoria_notificacao
AFTER INSERT OR UPDATE OR DELETE ON notificacao
FOR EACH ROW EXECUTE FUNCTION fn_auditoria_notificacao();



CREATE TABLE log_qualidade_dados (
    log_id BIGSERIAL PRIMARY KEY,
    notificacao_id BIGINT,
    regra_violada VARCHAR(255),
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2.2 Trigger Function para Validação Clínica (Regras de negócio epidemiológicas)
CREATE OR REPLACE FUNCTION fn_validacao_clinica()
RETURNS TRIGGER AS $$
BEGIN
    -- Regra 1: Homem gestante
    IF NEW.cs_sexo = 'M' AND NEW.cs_gestant IN (1, 2, 3) THEN
        INSERT INTO log_qualidade_dados (notificacao_id, regra_violada)
        VALUES (NEW.id, 'Paciente do sexo masculino com idade gestacional (cs_gestant 1, 2 ou 3)');
    END IF;

    -- Regra 2: Evolução por Óbito sem data
    IF NEW.evolucao IN (2, 3) AND NEW.dt_obito IS NULL THEN
        INSERT INTO log_qualidade_dados (notificacao_id, regra_violada)
        VALUES (NEW.id, 'Evolução para óbito (2 ou 3) sem dt_obito preenchido');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Acionador (Trigger) de Validação
CREATE TRIGGER trg_validacao_clinica
BEFORE INSERT OR UPDATE ON notificacao
FOR EACH ROW EXECUTE FUNCTION fn_validacao_clinica();

-- Função: Resumo epidemiológico por UF e Ano
CREATE OR REPLACE FUNCTION fn_resumo_epidemiologico(p_ano INTEGER, p_uf VARCHAR(2))
RETURNS TABLE (
    ano INTEGER, 
    uf_sigla VARCHAR(2), 
    total_notificados BIGINT, 
    casos_confirmados BIGINT, 
    obitos_zika BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        n.nu_ano,
        d.sigla,
        COUNT(n.id) AS total_notificados,
        SUM(CASE WHEN n.classi_fin = 1 THEN 1 ELSE 0 END) AS casos_confirmados,
        SUM(CASE WHEN n.evolucao = 2 THEN 1 ELSE 0 END) AS obitos_zika
    FROM notificacao n
    JOIN dim_uf d ON n.sg_uf_not = d.codigo_ibge
    WHERE n.nu_ano = p_ano AND d.sigla = p_uf
    GROUP BY n.nu_ano, d.sigla;
END;
$$ LANGUAGE plpgsql STABLE;

-- Exemplo de uso: SELECT * FROM fn_resumo_epidemiologico(2023, 'SP');



-- 3.1 View: Série Temporal Semanal (Curva Epidêmica)
CREATE OR REPLACE VIEW vw_serie_temporal_semanal AS
SELECT 
    nu_ano AS ano, 
    sem_pri AS semana_epidemiologica, 
    COUNT(id) AS total_casos_confirmados
FROM notificacao
WHERE classi_fin = 1 -- Apenas confirmados (1)
GROUP BY nu_ano, sem_pri
ORDER BY nu_ano, sem_pri;

-- 3.2 View: Casos por UF e Ano (Visão Geográfica Temporal)
CREATE OR REPLACE VIEW vw_casos_uf_ano AS
SELECT 
    n.nu_ano AS ano, 
    d.sigla AS uf, 
    COUNT(n.id) AS total_casos
FROM notificacao n
LEFT JOIN dim_uf d ON n.sg_uf_not = d.codigo_ibge
WHERE n.classi_fin = 1
GROUP BY n.nu_ano, d.sigla
ORDER BY n.nu_ano DESC, total_casos DESC;

-- 3.3 View: Pirâmide Etária (Agrupamento por sexo e faixa etária)
CREATE OR REPLACE VIEW vw_piramide_etaria AS
WITH faixa_etaria_calc AS (
    SELECT
        cs_sexo,
        CASE
            WHEN fn_decodifica_idade_anos(nu_idade_n) BETWEEN 0 AND 9 THEN '00-09 Anos'
            WHEN fn_decodifica_idade_anos(nu_idade_n) BETWEEN 10 AND 19 THEN '10-19 Anos'
            WHEN fn_decodifica_idade_anos(nu_idade_n) BETWEEN 20 AND 29 THEN '20-29 Anos'
            WHEN fn_decodifica_idade_anos(nu_idade_n) BETWEEN 30 AND 39 THEN '30-39 Anos'
            WHEN fn_decodifica_idade_anos(nu_idade_n) BETWEEN 40 AND 49 THEN '40-49 Anos'
            WHEN fn_decodifica_idade_anos(nu_idade_n) BETWEEN 50 AND 59 THEN '50-59 Anos'
            WHEN fn_decodifica_idade_anos(nu_idade_n) >= 60 THEN '60+ Anos'
            ELSE 'Ignorado'
        END AS faixa
    FROM notificacao
    WHERE classi_fin = 1 AND cs_sexo IN ('M', 'F')
)
SELECT faixa, cs_sexo, COUNT(*) AS quantidade
FROM faixa_etaria_calc
GROUP BY faixa, cs_sexo
ORDER BY faixa ASC, cs_sexo ASC;

-- 3.4 View: Vigilância de Gestantes (Foco em microcefalia congênita)
CREATE OR REPLACE VIEW vw_vigilancia_gestantes AS
SELECT
    n.nu_ano AS ano,
    d.sigla AS uf,
    CASE n.cs_gestant
        WHEN 1 THEN '1º Trimestre'
        WHEN 2 THEN '2º Trimestre'
        WHEN 3 THEN '3º Trimestre'
    END AS trimestre_gestacional,
    COUNT(n.id) AS gestantes_confirmadas
FROM notificacao n
LEFT JOIN dim_uf d ON n.sg_uf_not = d.codigo_ibge
WHERE n.classi_fin = 1 
  AND n.cs_sexo = 'F' 
  AND n.cs_gestant IN (1, 2, 3)
GROUP BY n.nu_ano, d.sigla, n.cs_gestant;

-- 3.5 View: Cards de KPI (Resumo rápido do cenário atual)
CREATE OR REPLACE VIEW vw_kpi_cards AS
SELECT
    (SELECT COUNT(id) FROM notificacao) AS total_notificacoes_gerais,
    (SELECT COUNT(id) FROM notificacao WHERE classi_fin = 1) AS total_casos_confirmados,
    (SELECT COUNT(id) FROM notificacao WHERE evolucao = 2) AS total_obitos_zika,
    (SELECT COUNT(id) FROM notificacao WHERE classi_fin = 1 AND cs_sexo = 'F' AND cs_gestant IN (1,2,3)) AS total_gestantes_em_risco;


-- 3.6 View: Evolução dos Casos (Desfecho)
CREATE OR REPLACE VIEW vw_evolucao_casos AS
SELECT 
    CASE evolucao 
        WHEN 1 THEN 'Cura'
        WHEN 2 THEN 'Óbito pelo agravo'
        WHEN 3 THEN 'Óbito por outras causas'
        WHEN 9 THEN 'Ignorado'
        ELSE 'Em Branco / Sem Informação'
    END AS tipo_evolucao,
    COUNT(id) AS total_casos
FROM notificacao
WHERE classi_fin = 1
GROUP BY evolucao
ORDER BY total_casos DESC;

-- 3.7 View: Tempo Médio de Notificação (Sintomas vs Notificação) por Ano
CREATE OR REPLACE VIEW vw_tempo_notificacao_ano AS
SELECT 
    nu_ano AS ano,
    ROUND(AVG(dt_notific - dt_sin_pri), 1) AS media_dias_notificacao
FROM notificacao
WHERE classi_fin = 1 
  AND dt_notific >= dt_sin_pri 
  AND (dt_notific - dt_sin_pri) <= 365 -- Filtro para evitar erros de digitação absurdos no SINAN (>1 ano)
GROUP BY nu_ano
ORDER BY nu_ano;

-- 3.8 View: Distribuição por Raça/Cor
CREATE OR REPLACE VIEW vw_raca_cor AS
SELECT 
    CASE cs_raca 
        WHEN 1 THEN 'Branca'
        WHEN 2 THEN 'Preta'
        WHEN 3 THEN 'Amarela'
        WHEN 4 THEN 'Parda'
        WHEN 5 THEN 'Indígena'
        WHEN 9 THEN 'Ignorado'
        ELSE 'Sem Informação'
    END AS raca_cor,
    COUNT(id) AS total_casos
FROM notificacao
WHERE classi_fin = 1
GROUP BY cs_raca
ORDER BY total_casos DESC;
```

### Passo 1: Configuração do Banco de Dados
Certifique-se de que o banco de dados `zika_db` foi populado. As views essenciais pré-agregadas devem existir no seu banco:
- `vw_kpi_cards`
- `vw_serie_temporal_semanal`
- `vw_casos_uf_ano`
- `vw_piramide_etaria`
- `vw_vigilancia_gestantes`
- `vw_evolucao_casos`
- `vw_tempo_notificacao_ano`
- `vw_raca_cor`

### Passo 2: Clonar o Repositório
Abra o seu terminal e rode os seguintes comandos:
```bash
git clone https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
cd SEU_REPOSITORIO
```

### Passo 3: Variáveis de Ambiente
Na raiz do projeto, crie um arquivo chamado `.env` e configure as credenciais de conexão do seu PostgreSQL:
```
DB_HOST=127.0.0.1
DB_PORT=5432
DB_NAME=zika_db
DB_USER=seu_usuario_postgres
DB_PASSWORD=sua_senha
```

### Passo 4: Instalar as Dependências
É altamente recomendável criar um ambiente virtual (venv). Após criar, instale os pacotes necessários contidos no `requirements.txt`:
```bash
# Opcional (Criar ambiente virtual)
python -m venv venv
venv\Scripts\activate  # No Windows
# source venv/bin/activate # No Linux/Mac
# Instalar pacotes
pip install -r requirements.txt
```

### Passo 5: Rodar a Aplicação
Com tudo instalado, levante o servidor do Streamlit:
```bash
streamlit run app.py
```

O seu navegador padrão abrirá automaticamente na porta `http://localhost:8501` rodando o painel de forma interativa.

---

## 📊 Novo: Análise Estatística Avançada

A partir da versão 1.1, o dashboard inclui um módulo completo de **Análise Estatística Avançada** com modelos de machine learning e previsão:

### 🌊 Sazonalidade e Decomposição Temporal
- Identifica padrões sazonais repetitivos
- Decomposição STL (Seasonal and Trend)
- Análise de amplitude sazonal e força de tendência
- Requisito: Mínimo 24 dias de dados

### 🔮 Previsão de Casos (Prophet)
- Modelo Facebook Prophet para previsão de 1-24 meses
- Intervalo de confiança automático (95%)
- Sazonalidade semanal e anual
- Requer: Mínimo 10 dias de dados históricos

### 📈 Análise de Tendência por UF
- Cálculo de variação percentual últimos 30 dias
- Média móvel de 7 dias
- Classificação automática de risco (crescente/estável/decrescente)
- Visualizações comparativas por estado

### 🗺️ Agrupamento de Municípios (K-Means)
- Clustering automático de 2-10 grupos
- Baseado em características epidemiológicas (incidência, gestantes)
- Classificação de risco por cluster
- Visualização 2D com PCA e gráficos de perfil

### 🔧 Novos Pacotes Instalados
```bash
pip install prophet>=1.1.5 scikit-learn>=1.3.0 scipy>=1.10.0 statsmodels>=0.14.0
```

Para mais detalhes, veja:
- 📖 [Documentação Completa](./ANALISE_ESTATISTICA_DOCS.md)
- 📋 [Guia de Instalação](./GUIA_INSTALACAO.md)
- 🚀 [Resumo Técnico](./IMPLEMENTACAO_SUMARIO.md)
- ✅ [Checklist](./CHECKLIST_IMPLEMENTACAO.md)
