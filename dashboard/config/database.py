import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import psycopg2
from sqlalchemy import create_engine

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "zika_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "110723")

@st.cache_resource
def get_engine():
    """Cria uma engine com o banco de dados PostgreSQL usando SQLAlchemy."""
    try:
        db_url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(db_url)
        return engine
    except Exception as e:
        st.error(f"Erro ao criar engine do banco de dados: {e}")
        return None

@st.cache_data(ttl=3600)
def fetch_data(query: str) -> pd.DataFrame:
    """Executa uma query no banco de dados e retorna um DataFrame do Pandas.
       A resposta é mantida em cache por 1 hora."""
    engine = get_engine()
    if engine is not None:
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            st.error(f"Erro ao buscar dados: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def apply_dynamic_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Aplica os filtros globais definidos no sidebar ao dataframe especificado,
    MAS apenas se as colunas necessárias existirem na view (já que agora usamos views pré-agregadas).
    """
    if df.empty:
        return df
        
    filtered_df = df.copy()
    
    if filters.get("ano") and 'ano' in filtered_df.columns:
        # Converte para numérico para garantir a compatibilidade do isin
        anos_filtro = [int(x) for x in filters['ano']]
        filtered_df = filtered_df[pd.to_numeric(filtered_df['ano'], errors='coerce').isin(anos_filtro)]
        
    if filters.get("uf") and 'uf' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['uf'].isin(filters['uf'])]
        
    if filters.get("sexo") and 'cs_sexo' in filtered_df.columns:
        # Se a view tem cs_sexo, garantimos que mapeie com os filtros M/F
        # O filtro retorna 'M' e 'F' se usarmos essas strings
        filtered_df = filtered_df[filtered_df['cs_sexo'].isin(filters['sexo'])]
        
    return filtered_df
