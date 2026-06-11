-- =============================================================
-- ETAPA 1 — Índices de performance
-- Executado pelo setup.py APÓS a carga dos dados.
-- (Criar índices antes de inserir 236 mil linhas é muito mais lento)
-- =============================================================

-- Filtro mais comum em qualquer análise: casos confirmados
CREATE INDEX IF NOT EXISTS idx_classi_fin
    ON notificacao (classi_fin);

-- Curva epidêmica — sempre se usa dt_sin_pri ou sem_pri
CREATE INDEX IF NOT EXISTS idx_dt_sin_pri
    ON notificacao (dt_sin_pri);

CREATE INDEX IF NOT EXISTS idx_sem_pri_ano
    ON notificacao (sem_pri, nu_ano);

-- Filtros regionais
CREATE INDEX IF NOT EXISTS idx_sg_uf_not
    ON notificacao (sg_uf_not);

CREATE INDEX IF NOT EXISTS idx_sg_uf
    ON notificacao (sg_uf);

CREATE INDEX IF NOT EXISTS idx_id_municip
    ON notificacao (id_municip);

-- Vigilância de gestantes
CREATE INDEX IF NOT EXISTS idx_gestante
    ON notificacao (cs_gestant)
    WHERE cs_gestant IN (1, 2, 3);

-- Óbitos
CREATE INDEX IF NOT EXISTS idx_evolucao
    ON notificacao (evolucao);

-- Índice composto: o mais frequente nas views do painel —
-- confirmados por UF de residência e ano
CREATE INDEX IF NOT EXISTS idx_confirmados_uf_ano
    ON notificacao (classi_fin, sg_uf, nu_ano)
    WHERE classi_fin = 1;
