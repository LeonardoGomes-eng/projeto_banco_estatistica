-- =============================================================
-- ETAPA 1 — Schema do banco ZIKA_BR_2018_2026
-- Executado automaticamente pelo setup.py
-- =============================================================

SET client_encoding = 'UTF8';

-- =============================================================
-- 1. TABELAS DE DOMÍNIO
-- Guardam os códigos e seus significados.
-- Evitam repetir strings como "Confirmado" em 236 mil linhas
-- e garantem que nenhum valor inválido entre na tabela principal.
-- =============================================================

CREATE TABLE IF NOT EXISTS dom_sexo (
    codigo    CHAR(1)     PRIMARY KEY,
    descricao VARCHAR(20) NOT NULL
);
INSERT INTO dom_sexo VALUES
    ('M', 'Masculino'),
    ('F', 'Feminino'),
    ('I', 'Ignorado')
ON CONFLICT DO NOTHING;

-- ---

CREATE TABLE IF NOT EXISTS dom_gestante (
    codigo    SMALLINT    PRIMARY KEY,
    descricao VARCHAR(50) NOT NULL
);
INSERT INTO dom_gestante VALUES
    (1, '1º trimestre'),
    (2, '2º trimestre'),
    (3, '3º trimestre'),
    (4, 'Idade gestacional ignorada'),
    (5, 'Não gestante'),
    (6, 'Não se aplica'),
    (9, 'Ignorado')
ON CONFLICT DO NOTHING;

-- ---

CREATE TABLE IF NOT EXISTS dom_raca (
    codigo    SMALLINT    PRIMARY KEY,
    descricao VARCHAR(30) NOT NULL
);
INSERT INTO dom_raca VALUES
    (1, 'Branca'),
    (2, 'Preta'),
    (3, 'Amarela'),
    (4, 'Parda'),
    (5, 'Indígena'),
    (9, 'Ignorado')
ON CONFLICT DO NOTHING;

-- ---

CREATE TABLE IF NOT EXISTS dom_escolaridade (
    codigo    SMALLINT    PRIMARY KEY,
    descricao VARCHAR(60) NOT NULL
);
INSERT INTO dom_escolaridade VALUES
    (0,  'Analfabeto'),
    (1,  '1ª a 4ª série incompleta do EF'),
    (2,  '4ª série completa do EF'),
    (3,  '5ª a 8ª série incompleta do EF'),
    (4,  'Ensino Fundamental completo'),
    (5,  'Ensino Médio incompleto'),
    (6,  'Ensino Médio completo'),
    (7,  'Educação superior incompleta'),
    (8,  'Educação superior completa'),
    (9,  'Ignorado'),
    (10, 'Não se aplica')
ON CONFLICT DO NOTHING;

-- ---

CREATE TABLE IF NOT EXISTS dom_classificacao_final (
    codigo    SMALLINT    PRIMARY KEY,
    descricao VARCHAR(30) NOT NULL
);
INSERT INTO dom_classificacao_final VALUES
    (0, 'Descartado'),
    (1, 'Confirmado'),
    (2, 'Em investigação'),
    (8, 'Inconclusivo')
ON CONFLICT DO NOTHING;

-- ---

CREATE TABLE IF NOT EXISTS dom_criterio (
    codigo    SMALLINT    PRIMARY KEY,
    descricao VARCHAR(40) NOT NULL
);
INSERT INTO dom_criterio VALUES
    (0, 'Em investigação'),
    (1, 'Laboratorial'),
    (2, 'Clínico-epidemiológico')
ON CONFLICT DO NOTHING;

-- ---

CREATE TABLE IF NOT EXISTS dom_evolucao (
    codigo    SMALLINT    PRIMARY KEY,
    descricao VARCHAR(30) NOT NULL
);
INSERT INTO dom_evolucao VALUES
    (0, 'Em investigação'),
    (1, 'Cura'),
    (2, 'Óbito pelo agravo'),
    (3, 'Óbito por outra causa'),
    (9, 'Ignorado')
ON CONFLICT DO NOTHING;

-- ---

CREATE TABLE IF NOT EXISTS dom_autoctonia (
    codigo    SMALLINT    PRIMARY KEY,
    descricao VARCHAR(30) NOT NULL
);
INSERT INTO dom_autoctonia VALUES
    (1, 'Autóctone'),
    (2, 'Importado'),
    (3, 'Indeterminado')
ON CONFLICT DO NOTHING;

-- =============================================================
-- 2. TABELA DIMENSÃO: UF
-- Códigos IBGE de 2 dígitos + sigla + nome + região.
-- Usada por JOIN nas análises e views do painel.
-- =============================================================

CREATE TABLE IF NOT EXISTS dim_uf (
    codigo_ibge SMALLINT    PRIMARY KEY,
    sigla       CHAR(2)     NOT NULL,
    nome        VARCHAR(40) NOT NULL,
    regiao      VARCHAR(15) NOT NULL
);
INSERT INTO dim_uf VALUES
    (11,'RO','Rondônia','Norte'),
    (12,'AC','Acre','Norte'),
    (13,'AM','Amazonas','Norte'),
    (14,'RR','Roraima','Norte'),
    (15,'PA','Pará','Norte'),
    (16,'AP','Amapá','Norte'),
    (17,'TO','Tocantins','Norte'),
    (21,'MA','Maranhão','Nordeste'),
    (22,'PI','Piauí','Nordeste'),
    (23,'CE','Ceará','Nordeste'),
    (24,'RN','Rio Grande do Norte','Nordeste'),
    (25,'PB','Paraíba','Nordeste'),
    (26,'PE','Pernambuco','Nordeste'),
    (27,'AL','Alagoas','Nordeste'),
    (28,'SE','Sergipe','Nordeste'),
    (29,'BA','Bahia','Nordeste'),
    (31,'MG','Minas Gerais','Sudeste'),
    (32,'ES','Espírito Santo','Sudeste'),
    (33,'RJ','Rio de Janeiro','Sudeste'),
    (35,'SP','São Paulo','Sudeste'),
    (41,'PR','Paraná','Sul'),
    (42,'SC','Santa Catarina','Sul'),
    (43,'RS','Rio Grande do Sul','Sul'),
    (50,'MS','Mato Grosso do Sul','Centro-Oeste'),
    (51,'MT','Mato Grosso','Centro-Oeste'),
    (52,'GO','Goiás','Centro-Oeste'),
    (53,'DF','Distrito Federal','Centro-Oeste')
ON CONFLICT DO NOTHING;

-- =============================================================
-- 3. TABELA PRINCIPAL: notificacao
-- Cada linha = uma ficha de notificação do SINAN.
-- Chaves estrangeiras garantem integridade referencial
-- com as tabelas de domínio acima.
-- =============================================================

CREATE TABLE IF NOT EXISTS notificacao (

    -- Chave primária gerada automaticamente
    id              BIGSERIAL   PRIMARY KEY,

    -- Rastreabilidade do arquivo de origem
    arquivo_origem  VARCHAR(30),
    ano_arquivo     SMALLINT,

    -- Identificação do agravo (CID-10: A92. / A928 = Zika)
    tp_not          SMALLINT,
    id_agravo       VARCHAR(10),

    -- Datas e semanas epidemiológicas
    dt_notific      DATE,
    sem_not         SMALLINT,
    nu_ano          SMALLINT,
    dt_sin_pri      DATE,       -- data dos primeiros sintomas (base para curva epidêmica)
    sem_pri         SMALLINT,   -- semana epidemiológica dos sintomas

    -- Localização da notificação
    sg_uf_not       SMALLINT    REFERENCES dim_uf(codigo_ibge),
    id_municip      INTEGER,
    id_regiona      INTEGER,

    -- Dados do paciente
    nu_idade_n      INTEGER,    -- idade codificada (ver decode_idade na Etapa 2)
    cs_sexo         CHAR(1)     REFERENCES dom_sexo(codigo),
    cs_gestant      SMALLINT    REFERENCES dom_gestante(codigo),
    cs_raca         SMALLINT    REFERENCES dom_raca(codigo),
    cs_escol_n      SMALLINT    REFERENCES dom_escolaridade(codigo),
    ano_nasc        INTEGER,
    id_ocupa_n      VARCHAR(10),

    -- Localização de residência
    sg_uf           SMALLINT    REFERENCES dim_uf(codigo_ibge),
    id_mn_resi      INTEGER,
    id_rg_resi      INTEGER,
    id_pais         INTEGER,

    -- Localização provável de infecção
    tpautocto       SMALLINT    REFERENCES dom_autoctonia(codigo),
    coufinf         INTEGER,
    copaisinf       INTEGER,
    comuninf        INTEGER,

    -- Classificação do caso
    classi_fin      SMALLINT    REFERENCES dom_classificacao_final(codigo),
    criterio        SMALLINT    REFERENCES dom_criterio(codigo),

    -- Evolução
    evolucao        SMALLINT    REFERENCES dom_evolucao(codigo),
    dt_obito        DATE,

    -- Datas administrativas
    dt_invest       DATE,
    dt_encerra      DATE,
    dt_digita       DATE,

    -- Campos de controle
    nduplic_n       SMALLINT,
    in_vincula      SMALLINT,
    doenca_tra      SMALLINT,
    cs_flxret       VARCHAR(5),
    flxrecebi       VARCHAR(5),
    tp_sistema      SMALLINT,
    tpuninot        SMALLINT,
    id_unidade      INTEGER


    -- sem_not e sem_pri vêm no formato AAASS no CSV (ex: 1805 = ano 2018 semana 05)
    -- constraints de range removidos para compatibilidade com o dado real
);

-- =============================================================
-- 4. TABELA DE AUDITORIA
-- Criada aqui para que o schema seja auto-suficiente.
-- Os triggers que a preenchem ficam na Etapa 2.
-- =============================================================

CREATE TABLE IF NOT EXISTS auditoria_notificacao (
    audit_id        BIGSERIAL   PRIMARY KEY,
    operacao        CHAR(6)     NOT NULL,       -- INSERT / UPDATE / DELETE
    notificacao_id  BIGINT,
    usuario         VARCHAR(50) DEFAULT current_user,
    momento         TIMESTAMPTZ DEFAULT now(),
    dado_anterior   JSONB,
    dado_posterior  JSONB
);
