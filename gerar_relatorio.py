import pandas as pd
from datetime import datetime

def duracao_para_segundos(dur_str):
    """Converte string HH:MM:SS para total em segundos."""
    try:
        partes = str(dur_str).split(':')
        return int(partes[0]) * 3600 + int(partes[1]) * 60 + int(partes[2])
    except:
        return 0

def formatar_segundos_para_tempo(total_seg):
    """Converte total de segundos em formato legível (ex: 1h 20m 15s ou 15m 30s)."""
    if pd.isna(total_seg) or total_seg <= 0:
        return "00:00:00"
    total_sec = int(round(total_seg))
    horas = total_sec // 3600
    minutos = (total_sec % 3600) // 60
    secs = total_sec % 60
    if horas > 0:
        return f"{horas}h {minutos}m {secs}s"
    return f"{minutos}m {secs}s"

def reavaliar_status_solucao(row):
    """
    Ajusta o status de solução: Se o agente respondeu e prestou a orientação, 
    o encerramento sem réplica do eleitor é considerado atendimento CONCLUÍDO/RESOLVIDO.
    """
    status_orig = str(row.get('status_solucao', ''))
    resumo = str(row.get('resumo_atendimento', '')).lower()
    resposto = row.get('Resposto_Por_Agente', True)
    
    if status_orig == 'Teste/Desconsiderado':
        return 'Teste/Desconsiderado'
    if status_orig == 'Resolvido':
        return 'Resolvido'
    
    # Reavaliação de atendimentos marcados como Não Resolvido por abandono pós-informação
    if resposto:
        termos_informacao_prestada = ['informou', 'explicou', 'orientou', 'esclareceu', 'forneceu', 'encaminhou', 'confirmou', 'instruiu']
        termos_falha_agente = ['sem resposta do operador', 'não respondeu', 'deixou de responder', 'agente não respondeu']
        
        if any(term in resumo for term in termos_informacao_prestada):
            if not any(falha in resumo for falha in termos_falha_agente):
                return 'Resolvido'
                
    return 'Não Resolvido'

def gerar_relatorio_html(df_filtrado, periodo_str="24/09/2026 a 06/10/2026"):
    """
    Gera o relatório executivo oficial em HTML com introdução institucional,
    métricas recalibradas, análise de horários e tabelas de conformidade.
    """
    df_analise = df_filtrado.copy()
    total_atendimentos = len(df_analise)
    
    if total_atendimentos == 0:
        return "<html><body><h1>Nenhum dado encontrado para os filtros selecionados.</h1></body></html>"

    # Aplicação da regra ajustada de resolução
    if 'status_solucao' in df_analise.columns:
        df_analise['status_solucao_efetivo'] = df_analise.apply(reavaliar_status_solucao, axis=1)
    else:
        df_analise['status_solucao_efetivo'] = 'Resolvido'

    # --- 1. MÉTRICAS PRINCIPAIS RECALCULADAS ---
    resolvidos = len(df_analise[df_analise['status_solucao_efetivo'] == 'Resolvido'])
    taxa_resolucao = (resolvidos / total_atendimentos * 100)
    
    atendimentos_audio = int(df_analise['Tem_Audio'].sum()) if 'Tem_Audio' in df_analise.columns else 0
    pct_audio = (atendimentos_audio / total_atendimentos * 100)

    sem_resposta = int((~df_analise['Resposto_Por_Agente']).sum()) if 'Resposto_Por_Agente' in df_analise.columns else 0
    pct_sem_resposta = (sem_resposta / total_atendimentos * 100)

    # Duração média dos contatos (TMA)
    df_analise['Duracao_Seg'] = df_analise['Duracao'].apply(duracao_para_segundos) if 'Duracao' in df_analise.columns else 0
    media_duracao_seg = df_analise['Duracao_Seg'].mean()
    tma_formatado = formatar_segundos_para_tempo(media_duracao_seg)

    # Ociosidade até encerramento
    tempo_encerramento_medio_seg = df_analise['Tempo_Ate_Encerramento_Seg'].mean() if 'Tempo_Ate_Encerramento_Seg' in df_analise.columns else 0
    tempo_encerramento_formatado = formatar_segundos_para_tempo(tempo_encerramento_medio_seg)

    # --- 2. DEMANDA POR HORÁRIO ---
    df_analise['Hora_Cheia'] = pd.to_datetime(df_analise['Hora_Inicio'], format='%H:%M:%S', errors='coerce').dt.hour
    picos = df_analise['Hora_Cheia'].value_counts().sort_index()
    
    if not picos.empty:
        hora_pico = picos.idxmax()
        qtd_pico = picos.max()
        hora_valida_picos = picos[picos > 0]
        hora_vale = hora_valida_picos.idxmin() if not hora_valida_picos.empty else picos.idxmin()
        qtd_vale = hora_valida_picos.min() if not hora_valida_picos.empty else picos.min()
        texto_horarios = f"O pico de atendimento ocorreu às <strong>{hora_pico:02d}h</strong> (com {qtd_pico} chamadas), enquanto a menor demanda concentrou-se às <strong>{hora_vale:02d}h</strong> ({qtd_vale} chamadas)."
    else:
        texto_horarios = "Dados insuficientes para análise temporal por hora."

    # --- 3. DADOS PARA TABELA DE ASSUNTOS ---
    matriz_assuntos_html = ""
    if 'assunto_principal' in df_analise.columns:
        crosstab_assuntos = pd.crosstab(df_analise['assunto_principal'], df_analise['status_solucao_efetivo'])
        for assunto, row in crosstab_assuntos.iterrows():
            qtd_res = row.get('Resolvido', 0)
            qtd_nao_res = row.get('Não Resolvido', 0)
            qtd_outros = row.sum() - (qtd_res + qtd_nao_res)
            taxa_assunto = (qtd_res / row.sum() * 100) if row.sum() > 0 else 0
            
            matriz_assuntos_html += f"""
            <tr>
                <td><strong>{assunto}</strong></td>
                <td style="text-align: center;">{row.sum()}</td>
                <td style="text-align: center; color: #2e7d32; font-weight: bold;">{qtd_res}</td>
                <td style="text-align: center; color: #c62828;">{qtd_nao_res}</td>
                <td style="text-align: center;">{qtd_outros}</td>
                <td style="text-align: center;"><strong>{taxa_assunto:.1f}%</strong></td>
            </tr>
            """

    # --- 4. DADOS PARA TABELA DE PRODUTIVIDADE DOS ATENDENTES ---
    desempenho_agentes = ""
    if 'Agente' in df_analise.columns:
        agente_summary = df_analise.groupby('Agente').agg(
            Total=('Protocolo', 'count'),
            Resolvidos=('status_solucao_efetivo', lambda x: (x == 'Resolvido').sum()),
            Com_Audio=('Tem_Audio', lambda x: x.sum() if 'Tem_Audio' in x else 0)
        ).reset_index()
        agente_summary['Taxa'] = (agente_summary['Resolvidos'] / agente_summary['Total'] * 100).round(1)
        agente_summary = agente_summary.sort_values(by='Total', ascending=False)
        
        for _, row in agente_summary.iterrows():
            desempenho_agentes += f"""
            <tr>
                <td><strong>{row['Agente']}</strong></td>
                <td style="text-align: center;">{row['Total']}</td>
                <td style="text-align: center; color: #2e7d32; font-weight: bold;">{row['Resolvidos']}</td>
                <td style="text-align: center;">{row['Com_Audio']}</td>
                <td style="text-align: center;"><strong>{row['Taxa']}%</strong></td>
            </tr>
            """

    # --- 5. MONTAGEM DO HTML DO RELATÓRIO ---
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo - Serviço de Atendimento ao Eleitor (CRE / TRE-PB)</title>
        <style>
            @media print {{
                body {{ margin: 0; padding: 15px; font-size: 11pt; }}
                .no-print {{ display: none; }}
                .page-break {{ page-break-before: always; }}
            }}
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 40px;
                color: #2c3e50;
                line-height: 1.6;
                background-color: #ffffff;
            }}
            .header-container {{
                border-bottom: 3px solid #003366;
                padding-bottom: 15px;
                margin-bottom: 25px;
            }}
            h1 {{
                color: #003366;
                font-size: 22px;
                margin: 0 0 5px 0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .subhead {{
                color: #555;
                font-size: 14px;
                font-weight: 600;
            }}
            .intro-box {{
                background-color: #f8f9fa;
                border-left: 4px solid #003366;
                padding: 15px 20px;
                margin-bottom: 25px;
                font-size: 13.5px;
                text-align: justify;
            }}
            .note-box {{
                background-color: #fefce8;
                border-left: 4px solid #eab308;
                padding: 12px 16px;
                margin-bottom: 25px;
                font-size: 12.5px;
                color: #713f12;
            }}
            h2 {{
                color: #005599;
                font-size: 16px;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 6px;
                margin-top: 30px;
            }}
            .kpi-container {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin: 20px 0;
            }}
            .kpi-card {{
                background: #f4f7f9;
                border: 1px solid #dce4ec;
                border-left: 5px solid #005599;
                padding: 12px 15px;
                width: 30%;
                box-sizing: border-box;
                border-radius: 4px;
            }}
            .kpi-card h3 {{
                margin: 0;
                font-size: 11px;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .kpi-card p {{
                margin: 6px 0 0 0;
                font-size: 20px;
                font-weight: bold;
                color: #003366;
            }}
            .kpi-card small {{
                font-size: 11px;
                color: #777;
            }}
            .highlight-box {{
                background-color: #eef6fc;
                border: 1px solid #bce0fd;
                padding: 12px 15px;
                border-radius: 4px;
                margin: 20px 0;
                font-size: 13px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 12px;
                font-size: 13px;
            }}
            th, td {{
                border: 1px solid #e0e0e0;
                padding: 9px 12px;
            }}
            th {{
                background-color: #003366;
                color: white;
                font-weight: 600;
                text-align: left;
            }}
            tr:nth-child(even) {{
                background-color: #fafafa;
            }}
            .footer {{
                margin-top: 45px;
                font-size: 11px;
                color: #888;
                text-align: center;
                border-top: 1px solid #e0e0e0;
                padding-top: 12px;
            }}
        </style>
    </head>
    <body>

        <div class="header-container">
            <h1>⚖️ Tribunal Regional Eleitoral da Paraíba</h1>
            <div class="subhead">Corregedoria Regional Eleitoral — Serviço de Atendimento ao Eleitor (SAE)</div>
        </div>

        <div class="intro-box">
            <strong>RELATÓRIO EXECUTIVO DE ATENDIMENTO VIRTUAL</strong><br><br>
            Este relatório apresenta a análise das interações e conversas realizadas pelo <strong>Serviço de Atendimento ao Eleitor (SAE)</strong> da <strong>Corregedoria Regional Eleitoral do TRE-PB</strong> através da plataforma de atendimento virtual <strong>SZ Chat</strong>, no período de <strong>{periodo_str}</strong>. 
            O objetivo é fornecer uma visão gerencial sobre o volume de chamadas, principais demandas dos eleitores, desempenho da equipe de atendentes e conformidade dos dados em atendimento às diretrizes do Tribunal.
        </div>

        <div class="note-box">
            <strong>💡 Nota Metodológica sobre Resolutividade:</strong> Consideram-se atendimentos <strong>Resolvidos/Concluídos</strong> todas as interações nas quais o atendente prestou a informação técnica solicitada, prestou esclarecimento sobre vedações da legislação eleitoral ou forneceu o devido encaminhamento, ainda que o eleitor tenha se ausentado sem enviar mensagem de encerramento após receber a resposta.
        </div>

        <h2>📊 Resumo das Principais Métricas Analisadas</h2>

        <div class="kpi-container">
            <div class="kpi-card">
                <h3>Total de Atendimentos</h3>
                <p>{total_atendimentos}</p>
                <small>Protocolos no SZ Chat</small>
            </div>
            <div class="kpi-card">
                <h3>Duração Média (TMA)</h3>
                <p>{tma_formatado}</p>
                <small>Tempo médio de interação</small>
            </div>
            <div class="kpi-card">
                <h3>Taxa de Resolução Efetiva</h3>
                <p>{taxa_resolucao:.1f}%</p>
                <small>{resolvidos} demandas resolvidas/orientadas</small>
            </div>
            <div class="kpi-card">
                <h3>Mensagens de Áudio</h3>
                <p>{pct_audio:.1f}%</p>
                <small>{atendimentos_audio} atendimentos c/ áudio</small>
            </div>
            <div class="kpi-card">
                <h3>Sem Resposta Humana</h3>
                <p>{sem_resposta} <span style="font-size:13px; font-weight:normal;">({pct_sem_resposta:.1f}%)</span></p>
                <small>Encerrados no bot/fila</small>
            </div>
            <div class="kpi-card">
                <h3>Ociosidade de Encerramento</h3>
                <p>{tempo_encerramento_formatado}</p>
                <small>Tempo da última msg até fechar</small>
            </div>
        </div>

        <div class="highlight-box">
            ⏰ <strong>Análise de Distribuição Horária:</strong> {texto_horarios}
        </div>

        <h2>📌 Resolução de Demandas por Assunto Principal</h2>
        <table>
            <thead>
                <tr>
                    <th>Assunto Principal</th>
                    <th style="text-align: center;">Total Demanda</th>
                    <th style="text-align: center;">Solucionados / Orientados</th>
                    <th style="text-align: center;">Pendente / Não Resolvido</th>
                    <th style="text-align: center;">Outros / Testes</th>
                    <th style="text-align: center;">% Resolutividade</th>
                </tr>
            </thead>
            <tbody>
                {matriz_assuntos_html}
            </tbody>
        </table>

        <h2>👥 Desempenho e Produtividade da Equipe de Atendimento</h2>
        <table>
            <thead>
                <tr>
                    <th>Atendente</th>
                    <th style="text-align: center;">Atendimentos Realizados</th>
                    <th style="text-align: center;">Demandas Solucionadas</th>
                    <th style="text-align: center;">Atendimentos c/ Áudio</th>
                    <th style="text-align: center;">Taxa de Resolução</th>
                </tr>
            </thead>
            <tbody>
                {desempenho_agentes if desempenho_agentes else "<tr><td colspan='5' style='text-align:center;'>Sem dados disponíveis para o período.</td></tr>"}
            </tbody>
        </table>

        <div class="footer">
            Relatório emitido em {datetime.now().strftime('%d/%m/%Y às %H:%M')} | Sistema de Análise de Atendimento do TRE-PB com anonimização total de PII conforme a LGPD.
        </div>

    </body>
    </html>
    """
    return html_content