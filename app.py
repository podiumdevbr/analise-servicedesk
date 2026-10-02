import streamlit as st
import pandas as pd
import plotly.express as px
import os

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
    
    # Converte Data_Inicio para datetime para permitir filtragem por período
    if 'Data_Inicio' in df.columns:
        df['Data_Inicio_DT'] = pd.to_datetime(df['Data_Inicio'], dayfirst=True, errors='coerce')
    
    return df

df = carregar_dados()

if df is None or df.empty:
    st.error(f"Arquivo '{ARQUIVO_DADOS}' não encontrado ou vazio. Execute o pipeline_completo.py primeiro!")
    st.stop()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.image("https://www.tre-pb.jus.br/++theme++portlet_tre_pb/img/logo-tre-pb.png", width=200) # Logo institucional
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

# Filtro por Agente
agentes_disponiveis = ["Todos"] + sorted(df['Agente'].dropna().unique().tolist())
agente_selecionado = st.sidebar.selectbox("Filtrar por Atendente", agentes_disponiveis)

# Filtro por Assunto
assuntos_disponiveis = ["Todos"] + sorted(df['assunto_principal'].dropna().unique().tolist())
assunto_selecionado = st.sidebar.selectbox("Filtrar por Assunto", assuntos_disponiveis)

# Filtro por Status da Solução
status_disponiveis = ["Todos"] + sorted(df['status_solucao'].dropna().unique().tolist())
status_selecionado = st.sidebar.selectbox("Filtrar por Status", status_disponiveis)

# --- APLICANDO FILTROS ---
df_filtrado = df.copy()

if intervalo_datas and len(intervalo_datas) == 2:
    data_inicio_sel, data_fim_sel = intervalo_datas
    df_filtrado = df_filtrado[
        (df_filtrado['Data_Inicio_DT'].dt.date >= data_inicio_sel) &
        (df_filtrado['Data_Inicio_DT'].dt.date <= data_fim_sel)
    ]

if agente_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Agente'] == agente_selecionado]
if assunto_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['assunto_principal'] == assunto_selecionado]
if status_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['status_solucao'] == status_selecionado]

# --- TÉRCIO SUPERIOR: MÉTRICAS (KPIs) ---
st.title("📊 Painel Gerencial de Atendimento - Service Desk (TRE-PB)")
st.markdown("Análise inteligente de conversas e conformidade de atendimento local (LGPD).")

col1, col2, col3, col4 = st.columns(4)

total_atendimentos = len(df_filtrado)
resolvidos = len(df_filtrado[df_filtrado['status_solucao'] == 'Resolvido'])
taxa_resolucao = (resolvidos / total_atendimentos * 100) if total_atendimentos > 0 else 0

col1.metric("Total de Atendimentos", total_atendimentos)
col2.metric("Taxa de Resolução", f"{taxa_resolucao:.1f}%")
col3.metric("Atendimentos com Áudio", int(df_filtrado['Tem_Audio'].sum()))
col4.metric("Sem Resposta Humana", int((~df_filtrado['Resposto_Por_Agente']).sum()))

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

# --- HORÁRIOS DE PICO ---
st.subheader("⏰ Horários de Maior e Menor Demanda (Início dos Atendimentos)")
if not df_filtrado.empty and 'Hora_Inicio' in df_filtrado.columns:
    df_filtrado['Hora_Cheia'] = pd.to_datetime(df_filtrado['Hora_Inicio'], format='%H:%M:%S', errors='coerce').dt.hour
    picos_hora = df_filtrado['Hora_Cheia'].value_counts().sort_index().reset_index()
    picos_hora.columns = ['Hora', 'Quantidade']
    
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

# --- TABELA DETALHADA DE PROTOCOLOS ---
st.subheader("📋 Detalhamento dos Protocolos Analisados")

cols_exibicao = [
    'Protocolo', 'Data_Inicio', 'Hora_Inicio', 'Agente', 
    'assunto_principal', 'status_solucao', 'qualidade_atendimento', 
    'resumo_atendimento', 'Duracao'
]

if 'Historico_Limpo' in df_filtrado.columns:
    cols_exibicao.append('Historico_Limpo')

st.dataframe(
    df_filtrado[cols_exibicao],
    use_container_width=True
)

# Botão para download direto do Excel consolidado pelo dashboard
if os.path.exists("atendimentos_analisados.xlsx"):
    with open("atendimentos_analisados.xlsx", "rb") as file:
        st.download_button(
            label="📥 Baixar Planilha Consolidada (Excel)",
            data=file,
            file_name="atendimentos_analisados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )