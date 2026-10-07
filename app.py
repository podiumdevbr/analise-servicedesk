import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from gerar_relatorio import gerar_relatorio_html, reavaliar_status_solucao

# 1. Configuração Inicial da Página
st.set_page_config(
    page_title="Dashboard de Atendimentos SAE - CRE/TRE-PB",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚖️ Análise de Atendimentos — SAE / Corregedoria Regional Eleitoral")
st.caption("Plataforma SZ Chat | Período Oficial de Análise: 24/09/2026 a 06/10/2026")

# 2. Carregamento dos Dados com Cache e Recalibragem de Solução
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv('atendimentos_analisados.csv', encoding='utf-8-sig')
        # Aplica a regra ajustada de resolutividade (considera orientação prestada como resolvido)
        df['status_solucao_efetivo'] = df.apply(reavaliar_status_solucao, axis=1)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar 'atendimentos_analisados.csv': {e}")
        return pd.DataFrame()

df = carregar_dados()

if df.empty:
    st.warning("Nenhum dado encontrado no arquivo local para exibição.")
    st.stop()

# 3. Barra Lateral (Sidebar) com Filtros Avançados
st.sidebar.header("🔍 Filtros de Análise")

# Filtro por Agente / Atendente
lista_agentes = sorted(df['Agente'].dropna().unique().tolist()) if 'Agente' in df.columns else []
agentes_selecionados = st.sidebar.multiselect("Atendente / Operador:", lista_agentes, default=lista_agentes)

# Filtro por Assunto Principal
lista_assuntos = sorted(df['assunto_principal'].dropna().unique().tolist()) if 'assunto_principal' in df.columns else []
assuntos_selecionados = st.sidebar.multiselect("Assunto Principal:", lista_assuntos, default=lista_assuntos)

# Filtro por Status de Solução Efetivo
lista_status = sorted(df['status_solucao_efetivo'].dropna().unique().tolist()) if 'status_solucao_efetivo' in df.columns else []
status_selecionados = st.sidebar.multiselect("Status de Solução:", lista_status, default=lista_status)

# Filtro por Áudio
opcao_audio = st.sidebar.radio("Atendimentos com Áudio:", ["Todos", "Apenas com Áudio", "Apenas sem Áudio"])

# Filtro por Resposta do Agente
opcao_resposta = st.sidebar.radio("Resposta do Atendente:", ["Todos", "Respostos por Agente", "Sem Resposta Humana"])

# Aplicação dos Filtros ao DataFrame
df_filtrado = df.copy()

if agentes_selecionados:
    df_filtrado = df_filtrado[df_filtrado['Agente'].isin(agentes_selecionados)]

if assuntos_selecionados:
    df_filtrado = df_filtrado[df_filtrado['assunto_principal'].isin(assuntos_selecionados)]

if status_selecionados:
    df_filtrado = df_filtrado[df_filtrado['status_solucao_efetivo'].isin(status_selecionados)]

if opcao_audio == "Apenas com Áudio":
    df_filtrado = df_filtrado[df_filtrado['Tem_Audio'] == True]
elif opcao_audio == "Apenas sem Áudio":
    df_filtrado = df_filtrado[df_filtrado['Tem_Audio'] == False]

if opcao_resposta == "Respostos por Agente":
    df_filtrado = df_filtrado[df_filtrado['Resposto_Por_Agente'] == True]
elif opcao_resposta == "Sem Resposta Humana":
    df_filtrado = df_filtrado[df_filtrado['Resposto_Por_Agente'] == False]

# 4. Cartões Superior de Indicadores (KPIs)
total_atendimentos = len(df_filtrado)
resolvidos = len(df_filtrado[df_filtrado['status_solucao_efetivo'] == 'Resolvido'])
taxa_resolucao = (resolvidos / total_atendimentos * 100) if total_atendimentos > 0 else 0
com_audio = int(df_filtrado['Tem_Audio'].sum()) if 'Tem_Audio' in df_filtrado.columns else 0
sem_resposta = int((~df_filtrado['Resposto_Por_Agente']).sum()) if 'Resposto_Por_Agente' in df_filtrado.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Atendimentos", total_atendimentos)
col2.metric("Taxa de Resolução Efetiva", f"{taxa_resolucao:.1f}%")
col3.metric("Atendimentos c/ Áudio", com_audio)
col4.metric("Sem Resposta Humana", sem_resposta)

st.markdown("---")

# 5. Organização em Abas (Tabs) para Navegação
aba_visao_geral, aba_equipe, aba_horarios, aba_relatorio, aba_dados = st.tabs([
    "📊 Visão Geral & Demandas", 
    "👥 Produtividade da Equipe", 
    "⏰ Distribuição Horária", 
    "📄 Relatório Executivo Oficial",
    "📋 Consulta de Atendimentos"
])

# --- ABA 1: VISÃO GERAL ---
with aba_visao_geral:
    st.subheader("Análise Geral de Assuntos e Soluções")
    c1, c2 = st.columns(2)
    
    with c1:
        if 'assunto_principal' in df_filtrado.columns:
            df_assunto = df_filtrado['assunto_principal'].value_counts().reset_index()
            df_assunto.columns = ['Assunto', 'Quantidade']
            fig_assunto = px.bar(
                df_assunto, 
                x='Quantidade', 
                y='Assunto', 
                orientation='h',
                title="Volume de Demandas por Assunto Principal",
                color='Quantidade',
                color_continuous_scale='Blues'
            )
            fig_assunto.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
            st.plotly_chart(fig_assunto, use_container_width=True)
            
    with c2:
        if 'assunto_principal' in df_filtrado.columns:
            df_status = df_filtrado.groupby(['assunto_principal', 'status_solucao_efetivo']).size().unstack(fill_value=0)
            fig_status = px.bar(
                df_status, 
                barmode='stack',
                title="Proporção de Resolução por Categoria",
                color_discrete_map={'Resolvido': '#2e7d32', 'Não Resolvido': '#c62828', 'Teste/Desconsiderado': '#757575'}
            )
            st.plotly_chart(fig_status, use_container_width=True)

# --- ABA 2: PRODUTIVIDADE DA EQUIPE ---
with aba_equipe:
    st.subheader("Desempenho Individual dos Atendentes")
    if 'Agente' in df_filtrado.columns:
        df_agente = df_filtrado.groupby('Agente').agg(
            Total=('Protocolo', 'count'),
            Resolvidos=('status_solucao_efetivo', lambda x: (x == 'Resolvido').sum()),
            Com_Audio=('Tem_Audio', lambda x: x.sum() if 'Tem_Audio' in x else 0)
        ).reset_index()
        df_agente['Taxa_Resolucao'] = (df_agente['Resolvidos'] / df_agente['Total'] * 100).round(1)
        df_agente = df_agente.sort_values(by='Total', ascending=False)
        
        st.dataframe(df_agente, use_container_width=True)
        
        fig_agente = px.bar(
            df_agente, 
            x='Agente', 
            y=['Resolvidos', 'Total'], 
            barmode='group',
            title="Total de Atendimentos vs Solucionados por Atendente",
            labels={'value': 'Quantidade', 'variable': 'Métrica'}
        )
        st.plotly_chart(fig_agente, use_container_width=True)

# --- ABA 3: DISTRIBUIÇÃO HORÁRIA ---
with aba_horarios:
    st.subheader("Análise Temporal de Chamadas")
    if 'Hora_Inicio' in df_filtrado.columns:
        df_filtrado['Hora_Cheia'] = pd.to_datetime(df_filtrado['Hora_Inicio'], format='%H:%M:%S', errors='coerce').dt.hour
        picos = df_filtrado['Hora_Cheia'].value_counts().sort_index().reset_index()
        picos.columns = ['Hora', 'Quantidade']
        
        fig_picos = px.line(
            picos, 
            x='Hora', 
            y='Quantidade', 
            markers=True, 
            title="Volume de Atendimentos por Horário do Dia",
            line_shape="spline"
        )
        fig_picos.update_xaxes(dtick=1)
        st.plotly_chart(fig_picos, use_container_width=True)

# --- ABA 4: RELATÓRIO EXECUTIVO OFICIAL ---
with aba_relatorio:
    st.subheader("Geração de Relatório Executivo Oficial em HTML/PDF")
    st.info("Este relatório reúne a introdução oficial, os dados consolidados e a metodologia de resolutividade pronta para apresentação à Corregedoria.")
    
    html_relatorio = gerar_relatorio_html(df_filtrado, periodo_str="24/09/2026 a 06/10/2026")
    
    st.download_button(
        label="📥 Baixar Relatório Executivo Completo (HTML / PDF)",
        data=html_relatorio,
        file_name="Relatorio_Executivo_SAE_CRE_TREPB.html",
        mime="text/html"
    )
    
    st.markdown("---")
    st.components.v1.html(html_relatorio, height=800, scrolling=True)

# --- ABA 5: CONSULTA DE DADOS DETALHADA ---
with aba_dados:
    st.subheader("Base de Dados de Atendimentos Analisados")
    
    busca_protocolo = st.text_input("🔎 Pesquisar por Protocolo ou Palavra-chave no Resumo:")
    df_exibicao = df_filtrado.copy()
    
    if busca_protocolo:
        df_exibicao = df_exibicao[
            df_exibicao['Protocolo'].astype(str).str.contains(busca_protocolo, case=False, na=False) |
            df_exibicao['resumo_atendimento'].astype(str).str.contains(busca_protocolo, case=False, na=False)
        ]
        
    colunas_exibir = ['Protocolo', 'Data', 'Hora_Inicio', 'Agente', 'assunto_principal', 'status_solucao_efetivo', 'Tem_Audio', 'resumo_atendimento']
    colunas_presentes = [c for c in colunas_exibir if c in df_exibicao.columns]
    
    st.dataframe(df_exibicao[colunas_presentes], use_container_width=True)