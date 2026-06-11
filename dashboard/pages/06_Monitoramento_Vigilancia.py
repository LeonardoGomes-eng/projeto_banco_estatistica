import streamlit as st
from config.database import fetch_data, apply_dynamic_filters
from components.charts import plot_tempo_notificacao
from queries.dashboard_queries import get_query_tempo_notificacao_ano

st.title("Monitoramento da Vigilância")
st.markdown("### Agilidade e Tempo de Resposta do Sistema de Saúde")

filtros = st.session_state.get("filtros_globais", {})

st.markdown('<div class="section-title">Tempo Médio de Notificação</div>', unsafe_allow_html=True)
st.write("A diferença em dias entre o início dos sintomas relatados pelo paciente e a efetiva notificação no SINAN. Quanto menor o tempo, mais rápida é a resposta do sistema de saúde para identificar e isolar surtos.")

df_tempo = fetch_data(get_query_tempo_notificacao_ano())

if not df_tempo.empty:
    # A view tem a coluna 'ano', então podemos aplicar o filtro dinâmico
    df_filtrado = apply_dynamic_filters(df_tempo, filtros)
    
    if not df_filtrado.empty:
        fig_tempo = plot_tempo_notificacao(df_filtrado)
        st.plotly_chart(fig_tempo, use_container_width=True)
        
        # Opcional: mostrar a média geral baseada no filtro
        media_geral = df_filtrado['media_dias_notificacao'].mean()
        st.metric("Média Geral do Período Selecionado", f"{media_geral:.1f} dias")
    else:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    st.warning("Falha ao carregar dados de tempo de notificação (vw_tempo_notificacao_ano).")

st.markdown("---")
st.info("💡 **Dica Analítica:** Quedas no atraso ao longo dos anos indicam melhorias na infraestrutura e treinamento epidemiológico local.")
