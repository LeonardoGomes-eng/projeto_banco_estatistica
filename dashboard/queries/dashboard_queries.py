def get_query_kpi_cards() -> str:
    return "SELECT * FROM vw_kpi_cards;"

def get_query_serie_temporal() -> str:
    return "SELECT * FROM vw_serie_temporal_semanal;"

def get_query_casos_uf_ano() -> str:
    return "SELECT * FROM vw_casos_uf_ano;"

def get_query_piramide_etaria() -> str:
    return "SELECT * FROM vw_piramide_etaria;"

def get_query_vigilancia_gestantes() -> str:
    return "SELECT * FROM vw_vigilancia_gestantes;"

def get_query_evolucao_casos() -> str:
    return "SELECT * FROM vw_evolucao_casos;"

def get_query_tempo_notificacao_ano() -> str:
    return "SELECT * FROM vw_tempo_notificacao_ano;"

def get_query_raca_cor() -> str:
    return "SELECT * FROM vw_raca_cor;"

def get_query_qualidade() -> str:
    return "SELECT * FROM log_qualidade_dados ORDER BY dt_verificacao DESC LIMIT 1000;"

def get_query_auditoria() -> str:
    return "SELECT * FROM auditoria_notificacao ORDER BY data_alteracao DESC LIMIT 1000;"

def get_query_inconsistencias_summary() -> str:
    return """
    SELECT tipo_inconsistencia, count(*) as total 
    FROM log_qualidade_dados 
    GROUP BY tipo_inconsistencia 
    ORDER BY total DESC;
    """

def get_query_auditoria_summary() -> str:
    return """
    SELECT operacao, count(*) as total 
    FROM auditoria_notificacao 
    GROUP BY operacao 
    ORDER BY total DESC;
    """
