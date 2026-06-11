"""
ETAPA 1 — Setup completo: schema + carga de dados
Projeto: Banco de Dados e Análise Epidemiológica — Zika SINAN 2018-2026

Como usar:
    1. Crie um banco vazio no pgAdmin (ex.: zika_db)
    2. Edite o arquivo .env com suas credenciais
    3. Coloque o CSV em data/ZIKA_BR_2018_2026_UNIFICADO.csv
    4. Execute:
           pip install psycopg2-binary pandas python-dotenv tqdm
           python setup.py
"""

import os
import sys
import logging
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from tqdm import tqdm

# ---------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------
BASE_DIR  = Path(__file__).parent
CSV_PATH  = BASE_DIR / "data" / "ZIKA_BR_2018_2026_UNIFICADO.csv"
SCHEMA_SQL = BASE_DIR / "etapa1" / "schema.sql"
INDICES_SQL = BASE_DIR / "etapa1" / "indices.sql"
BATCH_SIZE = 5_000

load_dotenv(BASE_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(BASE_DIR / "setup.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


def conectar():
    """Retorna uma conexão psycopg2 usando as credenciais do .env."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "zika_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
        )
        conn.autocommit = False
        return conn
    except psycopg2.OperationalError as e:
        log.error(f"Falha ao conectar ao banco: {e}")
        log.error("Verifique as credenciais no arquivo .env e se o PostgreSQL está rodando.")
        sys.exit(1)


def executar_sql_file(conn, path: Path):
    """Lê e executa um arquivo .sql inteiro."""
    log.info(f"Executando {path.name}...")
    sql = path.read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    log.info(f"{path.name} concluído.")


# ---------------------------------------------------------------
# Limpeza de valores por tipo
# ---------------------------------------------------------------

UFS_VALIDAS = {
    11,12,13,14,15,16,17,
    21,22,23,24,25,26,27,28,29,
    31,32,33,35,
    41,42,43,
    50,51,52,53,
}

def _inteiro(v):
    try:
        f = float(v)
        return None if pd.isna(f) else int(f)
    except (TypeError, ValueError):
        return None

def _smallint(v):
    """Converte para inteiro, mas retorna NULL se fora do range do SMALLINT (-32768 a 32767)."""
    n = _inteiro(v)
    if n is None:
        return None
    return n if -32768 <= n <= 32767 else None

def _semana_epidem(v):
    """Converte YYYYWW para YYWW para caber no SMALLINT."""
    n = _inteiro(v)
    if n is None:
        return None
    s = str(n)
    if len(s) == 6:
        n = int(s[2:])
    return n if -32768 <= n <= 32767 else None

def _uf(v):
    c = _inteiro(v)
    return c if c in UFS_VALIDAS else None

def _data(v):
    if pd.isna(v) if not isinstance(v, str) else v.strip() == "":
        return None
    d = pd.to_datetime(v, errors="coerce")
    return None if pd.isna(d) else d.date()

def _sexo(v):
    if pd.isna(v) if not isinstance(v, str) else False:
        return None
    s = str(v).strip().upper()
    return s if s in {"M", "F", "I"} else None

def _texto(v, limite=100):
    if pd.isna(v) if not isinstance(v, str) else v.strip() == "":
        return None
    return str(v).strip()[:limite]


# ---------------------------------------------------------------
# Mapeamento CSV → colunas SQL (ordem importa para o INSERT)
# ---------------------------------------------------------------

# Cada item: (nome_coluna_csv, nome_coluna_sql, função_limpeza)
MAPEAMENTO = [
    ("arquivo_origem", "arquivo_origem",  _texto),
    ("ano_arquivo",    "ano_arquivo",      _smallint),
    ("tp_not",         "tp_not",           _smallint),
    ("id_agravo",      "id_agravo",        _texto),
    ("dt_notific",     "dt_notific",       _data),
    ("sem_not",        "sem_not",          _semana_epidem),
    ("nu_ano",         "nu_ano",           _smallint),
    ("dt_sin_pri",     "dt_sin_pri",       _data),
    ("sem_pri",        "sem_pri",          _semana_epidem),
    ("sg_uf_not",      "sg_uf_not",        _uf),
    ("id_municip",     "id_municip",       _inteiro),
    ("id_regiona",     "id_regiona",       _inteiro),
    ("nu_idade_n",     "nu_idade_n",       _inteiro),
    ("cs_sexo",        "cs_sexo",          _sexo),
    ("cs_gestant",     "cs_gestant",       _smallint),
    ("cs_raca",        "cs_raca",          _smallint),
    ("cs_escol_n",     "cs_escol_n",       _smallint),
    ("ano_nasc",       "ano_nasc",         _inteiro),
    ("id_ocupa_n",     "id_ocupa_n",       _texto),
    ("sg_uf",          "sg_uf",            _uf),
    ("id_mn_resi",     "id_mn_resi",       _inteiro),
    ("id_rg_resi",     "id_rg_resi",       _inteiro),
    ("id_pais",        "id_pais",          _inteiro),
    ("tpautocto",      "tpautocto",        _smallint),
    ("coufinf",        "coufinf",          _inteiro),
    ("copaisinf",      "copaisinf",        _inteiro),
    ("comuninf",       "comuninf",         _inteiro),
    ("classi_fin",     "classi_fin",       _smallint),
    ("criterio",       "criterio",         _smallint),
    ("dt_invest",      "dt_invest",        _data),
    ("dt_encerra",     "dt_encerra",       _data),
    ("dt_digita",      "dt_digita",        _data),
    ("evolucao",       "evolucao",         _smallint),
    ("dt_obito",       "dt_obito",         _data),
    ("nduplic_n",      "nduplic_n",        _smallint),
    ("in_vincula",     "in_vincula",       _smallint),
    ("doenca_tra",     "doenca_tra",       _smallint),
    ("cs_flxret",      "cs_flxret",        _texto),
    ("flxrecebi",      "flxrecebi",        _texto),
    ("tp_sistema",     "tp_sistema",       _smallint),
    ("tpuninot",       "tpuninot",         _smallint),
    ("id_unidade",     "id_unidade",       _inteiro),
]

COLUNAS_SQL = [col_sql for _, col_sql, _ in MAPEAMENTO]

SQL_INSERT = f"""
    INSERT INTO notificacao ({', '.join(COLUNAS_SQL)})
    VALUES %s
    ON CONFLICT DO NOTHING
"""


def preparar_tupla(row: dict) -> tuple:
    resultado = []
    for col_csv, _, fn in MAPEAMENTO:
        resultado.append(fn(row.get(col_csv)))
    return tuple(resultado)


# ---------------------------------------------------------------
# Carga principal
# ---------------------------------------------------------------

def carregar_dados(conn):
    if not CSV_PATH.exists():
        log.error(f"CSV não encontrado: {CSV_PATH}")
        log.error("Coloque o arquivo em: data/ZIKA_BR_2018_2026_UNIFICADO.csv")
        sys.exit(1)

    log.info(f"Lendo CSV ({CSV_PATH.name})...")
    df = pd.read_csv(CSV_PATH, dtype=str, encoding="utf-8", low_memory=False)
    df.columns = df.columns.str.lower().str.strip()

    total = len(df)
    log.info(f"Total de registros no CSV: {total:,}")

    # Avisa sobre colunas ausentes (não aborta — vira NULL)
    faltando = [c for c, _, _ in MAPEAMENTO if c not in df.columns]
    if faltando:
        log.warning(f"Colunas ausentes no CSV (serão NULL): {faltando}")
    for col in faltando:
        df[col] = float("nan")

    registros = df.to_dict(orient="records")
    lotes = [registros[i:i + BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]

    inseridos = 0
    erros     = 0

    log.info(f"Carregando em lotes de {BATCH_SIZE:,}...")
    with conn.cursor() as cur:
        for lote in tqdm(lotes, desc="Carga", unit="lote"):
            tuplas = []
            for row in lote:
                try:
                    tuplas.append(preparar_tupla(row))
                except Exception as e:
                    erros += 1
                    log.debug(f"Erro ao preparar linha: {e}")

            try:
                execute_values(cur, SQL_INSERT, tuplas)
                conn.commit()
                inseridos += len(tuplas)
            except Exception as e:
                conn.rollback()
                erros += len(tuplas)
                log.error(f"Erro no lote: {e}")

    log.info("=" * 50)
    log.info(f"Carga concluída!")
    log.info(f"  Inseridos : {inseridos:,}")
    log.info(f"  Erros     : {erros:,}")
    log.info(f"  Total CSV : {total:,}")
    log.info("=" * 50)


# ---------------------------------------------------------------
# Verificação pós-carga
# ---------------------------------------------------------------

def verificar(conn):
    log.info("Verificando carga...")
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM notificacao")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM notificacao WHERE classi_fin = 1")
        confirmados = cur.fetchone()[0]

        cur.execute("""
            SELECT nu_ano, COUNT(*) AS casos
            FROM notificacao
            WHERE classi_fin = 1
            GROUP BY nu_ano
            ORDER BY nu_ano
        """)
        por_ano = cur.fetchall()

    log.info(f"Total na tabela   : {total:,}")
    log.info(f"Casos confirmados : {confirmados:,}")
    log.info("Confirmados por ano:")
    for ano, casos in por_ano:
        log.info(f"  {ano}: {casos:,}")


# ---------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------

if __name__ == "__main__":
    log.info("=== ETAPA 1 — Setup do banco Zika SINAN ===")

    conn = conectar()
    log.info("Conexão estabelecida.")

    executar_sql_file(conn, SCHEMA_SQL)
    carregar_dados(conn)
    executar_sql_file(conn, INDICES_SQL)
    verificar(conn)

    conn.close()
    log.info("Tudo pronto! Banco disponível para as etapas seguintes.")
