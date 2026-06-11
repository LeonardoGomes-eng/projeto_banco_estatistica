import streamlit as st
import pandas as pd
import plotly.express as px
from config.database import fetch_data
from components.kpi_cards import render_kpi_card
from queries.dashboard_queries import (
    get_query_qualidade, 
    get_query_auditoria,
    get_query_inconsistencias_summary,
    get_query_auditoria_summary
)

st.title("Qualidade de Dados & Auditoria")
st.markdown("### Monitoramento do Banco de Dados e Inconsistências")

tab1, tab2 = st.tabs(["🛡️ Auditoria (Triggers)", "📉 Qualidade de Dados (Clínica)"])

with tab1:
    st.markdown('<div class="section-title">Log de Operações (INSERT/UPDATE/DELETE)</div>', unsafe_allow_html=True)
    
    with st.spinner("Carregando logs de auditoria..."):
        df_audit_sum = fetch_data(get_query_auditoria_summary())
        
        if not df_audit_sum.empty and 'operacao' in df_audit_sum.columns:
            col1, col2, col3 = st.columns(3)
            
            # Conta INSERTs, UPDATEs, DELETEs
            inserts = df_audit_sum[df_audit_sum['operacao'] == 'INSERT']['total'].sum()
            updates = df_audit_sum[df_audit_sum['operacao'] == 'UPDATE']['total'].sum()
            deletes = df_audit_sum[df_audit_sum['operacao'] == 'DELETE']['total'].sum()
            
            with col1:
                render_kpi_card("Total de INSERTs", f"{inserts:,}", "➕")
            with col2:
                render_kpi_card("Total de UPDATEs", f"{updates:,}", "🔄")
            with col3:
                render_kpi_card("Total de DELETEs", f"{deletes:,}", "❌", trend="down")
                
            fig_audit = px.bar(
                df_audit_sum, 
                x='operacao', 
                y='total', 
                color='operacao',
                title="Resumo de Operações no Banco"
            )
            st.plotly_chart(fig_audit, use_container_width=True)
            
            st.markdown("#### Últimos Registros Auditados")
            df_audit_logs = fetch_data(get_query_auditoria())
            st.dataframe(df_audit_logs, use_container_width=True)
        else:
            st.info("Nenhuma tabela de auditoria encontrada ou tabela vazia.")

with tab2:
    st.markdown('<div class="section-title">Validação Clínica e Inconsistências</div>', unsafe_allow_html=True)
    
    with st.spinner("Carregando logs de qualidade..."):
        df_qualidade_sum = fetch_data(get_query_inconsistencias_summary())
        
        if not df_qualidade_sum.empty and 'tipo_inconsistencia' in df_qualidade_sum.columns:
            total_erros = df_qualidade_sum['total'].sum()
            
            st.metric("Total de Inconsistências Detectadas", f"{total_erros:,}")
            
            fig_qualidade = px.pie(
                df_qualidade_sum, 
                names='tipo_inconsistencia', 
                values='total',
                title="Distribuição dos Tipos de Inconsistência",
                hole=0.4
            )
            st.plotly_chart(fig_qualidade, use_container_width=True)
            
            st.markdown("#### Tabela Detalhada de Erros")
            df_qualidade_logs = fetch_data(get_query_qualidade())
            st.dataframe(df_qualidade_logs, use_container_width=True)
        else:
            st.info("Nenhum registro de inconsistência encontrado. Base de dados limpa!")
