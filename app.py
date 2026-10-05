import streamlit as st
import pandas as pd
import plotly.express as px
import os
from gerar_relatorio import gerar_relatorio_html, duracao_para_segundos, formatar_segundos_para_tempo

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Dashboard Service Desk - TRE-PB",
    page_icon="⚖️",
    layout="wide"
)

ARQUIVO_DADOS = "atendimentos_analisados.csv"

@st.cache_data
def carregar_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        return None
    df = pd.read_csv(ARQUIVO_DADOS, encoding='utf-8-sig')
    
    if 'Data_Inicio' in df.columns:
        df['Data_Inicio_DT'] = pd.to_datetime(df['Data_Inicio'], dayfirst=True, errors='coerce')
    
    return df

df = carregar_dados()

if df is None or df.empty:
    st.error(f"Arquivo '{ARQUIVO_DADOS}' não encontrado ou vazio. Execute o pipeline_completo.py primeiro!")
    st.stop()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.image("https://www.tre-pb.jus.br/++theme++portlet_tre_pb/img/logo-tre-pb.png", width=200)
st.sidebar.title("Filtros de Análise")

# --- FILTRO POR DATA ---
df_valido_datas = df.dropna(subset=['Data_Inicio_DT'])

if not df_valido_datas.empty:
    min_data = df_valido_datas['Data_Inicio_DT'].min().date()
    max_data = df_valido_datas['Data_Inicio_DT'].max().date()

    intervalo_datas = st.sidebar.date_input(
        "Filtrar por Período",
        value=(min_data, max_data),
        min_value=min_data,
        max_value=max_data,
        format="DD/MM/YYYY"
    )
else:
    intervalo_datas = None

# Filtros secundários
agentes_disponiveis = ["Todos"] + sorted(df['Agente'].dropna().unique().tolist())
agente_selecionado = st.sidebar.selectbox("Filtrar por Atendente", agentes_disponiveis)

assuntos_disponiveis = ["Todos"] + sorted(df['assunto_principal'].dropna().unique().tolist())
assunto_selecionado = st.sidebar.selectbox("Filtrar por Assunto", assuntos_disponiveis)

status_disponiveis = ["Todos"] + sorted(df['status_solucao'].dropna().unique().tolist())
status_selecionado = st.sidebar.selectbox("Filtrar por Status", status_disponiveis)

# --- APLICANDO FILTROS ---
df_filtrado = df.copy()

periodo_str = "Período Completo"
if intervalo_datas and len(intervalo_datas) == 2:
    data_inicio_sel, data_fim_sel = intervalo_datas
    df_filtrado = df_filtrado[
        (df_filtrado['Data_Inicio_DT'].dt.date >= data_inicio_sel) &
        (df_filtrado['Data_Inicio_DT'].dt.date <= data_fim_sel)
    ]
    periodo_str = f"{data_inicio_sel.strftime('%d/%m/%Y')} até {data_fim_sel.strftime('%d/%m/%Y')}"

if agente_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Agente'] == agente_selecionado]
if assunto_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['assunto_principal'] == assunto_selecionado]
if status_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['status_solucao'] == status_selecionado]

# --- GERAR RELATÓRIO EXECUTIVO ---
st.sidebar.markdown("---")
st.sidebar.subheader("📄 Relatório Executivo")

html_relatorio = gerar_relatorio_html(df_filtrado, periodo_str)

st.sidebar.download_button(
    label="📄 Baixar Relatório Executivo (HTML/PDF)",
    data=html_relatorio,
    file_name=f"relatorio_executivo_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.html",
    mime="text/html"
)

# --- TÉRCIO SUPERIOR: CÁLCULO DE MÉTRICAS COMPLETO ---
st.title("📊 Painel Gerencial de Atendimento - Service Desk (TRE-PB)")
st.markdown("Análise inteligente de conversas e conformidade de atendimento local (LGPD).")

total_atendimentos = len(df_filtrado)
resolvidos = len(df_filtrado[df_filtrado['status_solucao'] == 'Resolvido'])
taxa_resolucao = (resolvidos / total_atendimentos * 100) if total_atendimentos > 0 else 0

atendimentos_audio = int(df_filtrado['Tem_Audio'].sum()) if 'Tem_Audio' in df_filtrado.columns else 0
pct_audio = (atendimentos_audio / total_atendimentos * 100) if total_atendimentos > 0 else 0

sem_resposta = int((~df_filtrado['Resposto_Por_Agente']).sum()) if 'Resposto_Por_Agente' in df_filtrado.columns else 0

# Cálculos de tempo
df_filtrado['Duracao_Seg'] = df_filtrado['Duracao'].apply(duracao_para_segundos) if 'Duracao' in df_filtrado.columns else 0
media_duracao_seg = df_filtrado['Duracao_Seg'].mean() if total_atendimentos > 0 else 0
tma_formatado = formatar_segundos_para_tempo(media_duracao_seg)

tempo_encerramento_medio_seg = df_filtrado['Tempo_Ate_Encerramento_Seg'].mean() if 'Tempo_Ate_Encerramento_Seg' in df_filtrado.columns and total_atendimentos > 0 else 0
tempo_enc_formatado = formatar_segundos_para_tempo(tempo_encerramento_medio_seg)

# Exibição dos KPIs em 2 Linhas
kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
kpi_col1.metric("Total de Atendimentos", total_atendimentos)
kpi_col2.metric("Taxa de Resolução", f"{taxa_resolucao:.1f}%", help="Percentual de solicitações classificadas como Resolvido")
kpi_col3.metric("Duração Média (TMA)", tma_formatado, help="Tempo médio entre o aceite do atendente e o fim do chat")

kpi_col4, kpi_col5, kpi_col6 = st.columns(3)
kpi_col4.metric("Uso de Mensagem de Áudio", f"{pct_audio:.1f}%", f"{atendimentos_audio} chamadas com áudio")
kpi_col5.metric("Sem Resposta Humana", sem_resposta, help="Chamadas encerradas na fila sem contato com atendente")
kpi_col6.metric("Ociosidade de Encerramento", tempo_enc_formatado, help="Média de tempo entre a última fala e o fecho do chat")

st.markdown("---")

# --- SEÇÃO DE GRÁFICOS ---
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("📌 Distribuição por Assunto Principal")
    if not df_filtrado.empty:
        fig_assunto = px.pie(
            df_filtrado, 
            names='assunto_principal', 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        st.plotly_chart(fig_assunto, use_container_width=True)
    else:
        st.info("Sem dados para exibir no período/filtros selecionados.")

with col_g2:
    st.subheader("⚖️ Qualidade do Atendimento (Cordialidade)")
    if not df_filtrado.empty:
        fig_qualidade = px.bar(
            df_filtrado['qualidade_atendimento'].value_counts().reset_index(),
            x='qualidade_atendimento',
            y='count',
            labels={'qualidade_atendimento': 'Avaliação', 'count': 'Quantidade'},
            color='qualidade_atendimento',
            color_discrete_sequence=px.colors.sequential.Teal_r
        )
        st.plotly_chart(fig_qualidade, use_container_width=True)
    else:
        st.info("Sem dados para exibir no período/filtros selecionados.")

# --- HORÁRIOS DE PICO E MENOR DEMANDA ---
st.subheader("⏰ Horários de Demanda (Início dos Atendimentos)")
if not df_filtrado.empty and 'Hora_Inicio' in df_filtrado.columns:
    df_filtrado['Hora_Cheia'] = pd.to_datetime(df_filtrado['Hora_Inicio'], format='%H:%M:%S', errors='coerce').dt.hour
    picos_hora = df_filtrado['Hora_Cheia'].value_counts().sort_index().reset_index()
    picos_hora.columns = ['Hora', 'Quantidade']
    
    if not picos_hora.empty:
        h_pico = picos_hora.loc[picos_hora['Quantidade'].idxmax()]
        st.info(f"💡 **Destaque:** Maior volume concentrado às **{int(h_pico['Hora']):02d}h** ({int(h_pico['Quantidade'])} chamadas).")

    fig_hora = px.bar(
        picos_hora,
        x='Hora',
        y='Quantidade',
        labels={'Hora': 'Hora do Dia (00h - 23h)', 'Quantidade': 'Total de Chamadas'},
        text_auto=True,
        color_discrete_sequence=['#1f77b4']
    )
    fig_hora.update_layout(xaxis=dict(tickmode='linear', dtick=1))
    st.plotly_chart(fig_hora, use_container_width=True)

st.markdown("---")

# --- RESUMO EXECUTIVO NA TELA (EXPANSÍVEL) ---
with st.expander("📋 Visualizar Relatório Executivo Resumido na Tela", expanded=True):
    st.markdown(f"### Síntese Operacional ({periodo_str})")
    
    c_exp1, c_exp2 = st.columns(2)
    with c_exp1:
        st.markdown("**Status de Solução por Assunto Principal:**")
        if 'assunto_principal' in df_filtrado.columns and 'status_solucao' in df_filtrado.columns:
            tb_assuntos = pd.crosstab(df_filtrado['assunto_principal'], df_filtrado['status_solucao'], margins=True, margins_name="Total")
            st.dataframe(tb_assuntos, use_container_width=True)
    
    with c_exp2:
        st.markdown("**Desempenho por Atendente:**")
        if 'Agente' in df_filtrado.columns:
            ag_summary = df_filtrado.groupby('Agente').agg(
                Total=('Protocolo', 'count'),
                Resolvidos=('status_solucao', lambda x: (x == 'Resolvido').sum()),
                Com_Audio=('Tem_Audio', lambda x: x.sum() if 'Tem_Audio' in x else 0)
            ).reset_index()
            ag_summary['% Resolução'] = (ag_summary['Resolvidos'] / ag_summary['Total'] * 100).round(1)
            st.dataframe(ag_summary, use_container_width=True)

st.markdown("---")

# --- TABELA DETALHADA DE PROTOCOLOS ---
st.subheader("📋 Detalhamento dos Protocolos Analisados")

cols_exibicao = [
    'Protocolo', 'Data_Inicio', 'Hora_Inicio', 'Agente', 
    'assunto_principal', 'status_solucao', 'qualidade_atendimento', 
    'resumo_atendimento', 'Duracao', 'Tempo_Ate_Encerramento_Seg'
]

if 'Historico_Limpo' in df_filtrado.columns:
    cols_exibicao.append('Historico_Limpo')

st.dataframe(
    df_filtrado[cols_exibicao],
    use_container_width=True
)

if os.path.exists("atendimentos_analisados.xlsx"):
    with open("atendimentos_analisados.xlsx", "rb") as file:
        st.download_button(
            label="📥 Baixar Planilha Consolidada (Excel)",
            data=file,
            file_name="atendimentos_analisados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )