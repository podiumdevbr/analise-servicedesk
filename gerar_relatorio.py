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
    """Converte total de segundos de volta para o formato legível HH:MM:SS ou MMm SSs."""
    if pd.isna(total_seg) or total_seg <= 0:
        return "00:00:00"
    total_sec = int(round(total_seg))
    horas = total_sec // 3600
    minutos = (total_sec % 3600) // 60
    secs = total_sec % 60
    if horas > 0:
        return f"{horas}h {minutos}m {secs}s"
    return f"{minutos}m {secs}s"

def gerar_relatorio_html(df_filtrado, periodo_str="Período Geral"):
    total_atendimentos = len(df_filtrado)
    
    if total_atendimentos == 0:
        return "<html><body><h1>Nenhum dado encontrado para os filtros selecionados.</h1></body></html>"

    # 1. Taxa de Resolução
    resolvidos = len(df_filtrado[df_filtrado['status_solucao'] == 'Resolvido'])
    taxa_resolucao = (resolvidos / total_atendimentos * 100)
    
    # 2. Mensagens de Áudio (%)
    atendimentos_audio = int(df_filtrado['Tem_Audio'].sum()) if 'Tem_Audio' in df_filtrado.columns else 0
    pct_audio = (atendimentos_audio / total_atendimentos * 100)

    # 3. Chamadas Sem Resposta do Operador
    sem_resposta = int((~df_filtrado['Resposto_Por_Agente']).sum()) if 'Resposto_Por_Agente' in df_filtrado.columns else 0
    pct_sem_resposta = (sem_resposta / total_atendimentos * 100)

    # 4. Duração Média dos Contatos (TMA)
    df_filtrado['Duracao_Seg'] = df_filtrado['Duracao'].apply(duracao_para_segundos)
    media_duracao_seg = df_filtrado['Duracao_Seg'].mean()
    tma_formatado = formatar_segundos_para_tempo(media_duracao_seg)

    # 5. Tempo Médio entre Última Interação Humana e Encerramento
    tempo_encerramento_medio_seg = df_filtrado['Tempo_Ate_Encerramento_Seg'].mean() if 'Tempo_Ate_Encerramento_Seg' in df_filtrado.columns else 0
    tempo_encerramento_formatado = formatar_segundos_para_tempo(tempo_encerramento_medio_seg)

    # 6. Horários de Maior e Menor Demanda
    df_filtrado['Hora_Cheia'] = pd.to_datetime(df_filtrado['Hora_Inicio'], format='%H:%M:%S', errors='coerce').dt.hour
    picos = df_filtrado['Hora_Cheia'].value_counts().sort_index()
    
    if not picos.empty:
        hora_pico = picos.idxmax()
        qtd_pico = picos.max()
        hora_valida_picos = picos[picos > 0]
        hora_vale = hora_valida_picos.idxmin() if not hora_valida_picos.empty else picos.idxmin()
        qtd_vale = hora_valida_picos.min() if not hora_valida_picos.empty else picos.min()
        texto_horarios = f"Pico de demanda às <strong>{hora_pico:02d}h</strong> ({qtd_pico} chamadas) | Menor demanda às <strong>{hora_vale:02d}h</strong> ({qtd_vale} chamadas)."
    else:
        texto_horarios = "Dados insuficientes para análise de horários."

    # 7. Matriz de Assuntos: Solucionados vs Não Solucionados
    matriz_assuntos_html = ""
    if 'assunto_principal' in df_filtrado.columns and 'status_solucao' in df_filtrado.columns:
        crosstab_assuntos = pd.crosstab(df_filtrado['assunto_principal'], df_filtrado['status_solucao'])
        for assunto, row in crosstab_assuntos.iterrows():
            qtd_res = row.get('Resolvido', 0)
            qtd_nao_res = row.get('Não Resolvido', 0)
            qtd_outros = row.sum() - (qtd_res + qtd_nao_res)
            taxa_assunto = (qtd_res / row.sum() * 100) if row.sum() > 0 else 0
            
            matriz_assuntos_html += f"""
            <tr>
                <td><strong>{assunto}</strong></td>
                <td>{row.sum()}</td>
                <td style="color: green; font-weight: bold;">{qtd_res}</td>
                <td style="color: red;">{qtd_nao_res}</td>
                <td>{qtd_outros}</td>
                <td>{taxa_assunto:.1f}%</td>
            </tr>
            """

    # 8. Desempenho por Atendente
    desempenho_agentes = ""
    if 'Agente' in df_filtrado.columns:
        agente_summary = df_filtrado.groupby('Agente').agg(
            Total=('Protocolo', 'count'),
            Resolvidos=('status_solucao', lambda x: (x == 'Resolvido').sum()),
            Com_Audio=('Tem_Audio', lambda x: x.sum() if 'Tem_Audio' in x else 0)
        ).reset_index()
        agente_summary['Taxa'] = (agente_summary['Resolvidos'] / agente_summary['Total'] * 100).round(1)
        
        for _, row in agente_summary.iterrows():
            desempenho_agentes += f"<tr><td>{row['Agente']}</td><td>{row['Total']}</td><td>{row['Resolvidos']}</td><td>{row['Com_Audio']}</td><td>{row['Taxa']}%</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo - Service Desk TRE-PB</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; line-height: 1.4; }}
            h1 {{ color: #003366; border-bottom: 2px solid #003366; padding-bottom: 8px; margin-bottom: 5px; }}
            h2 {{ color: #005599; margin-top: 25px; font-size: 18px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
            .subhead {{ color: #666; font-size: 13px; margin-bottom: 20px; }}
            .kpi-container {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0; }}
            .kpi-card {{ background: #f4f7f9; border-left: 5px solid #005599; padding: 12px 15px; width: 30%; box-sizing: border-box; }}
            .kpi-card h3 {{ margin: 0; font-size: 12px; color: #555; text-transform: uppercase; }}
            .kpi-card p {{ margin: 5px 0 0 0; font-size: 20px; font-weight: bold; color: #003366; }}
            .kpi-card small {{ font-size: 11px; color: #777; }}
            .highlight-box {{ background-color: #eef6fc; border: 1px solid #bce0fd; padding: 12px 15px; border-radius: 4px; margin: 15px 0; font-size: 14px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; }}
            th {{ background-color: #003366; color: white; font-weight: 600; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .footer {{ margin-top: 40px; font-size: 11px; color: #777; text-align: center; border-top: 1px solid #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>⚖️ Tribunal Regional Eleitoral da Paraíba - TRE-PB</h1>
        <div class="subhead">
            <strong>Relatório Executivo de Auditoria e Qualidade do Service Desk</strong><br>
            Período Analisado: <strong>{periodo_str}</strong> | Emissão: <strong>{datetime.now().strftime('%d/%m/%Y %H:%M')}</strong>
        </div>

        <div class="kpi-container">
            <div class="kpi-card">
                <h3>Total de Chamadas</h3>
                <p>{total_atendimentos}</p>
                <small>Protocolos registrados</small>
            </div>
            <div class="kpi-card">
                <h3>Duração Média (TMA)</h3>
                <p>{tma_formatado}</p>
                <small>Tempo médio de contato</small>
            </div>
            <div class="kpi-card">
                <h3>Taxa de Resolução</h3>
                <p>{taxa_resolucao:.1f}%</p>
                <small>{resolvidos} resolvidos com sucesso</small>
            </div>
            <div class="kpi-card">
                <h3>Mensagens de Áudio</h3>
                <p>{pct_audio:.1f}%</p>
                <small>{atendimentos_audio} eleitores enviaram áudio</small>
            </div>
            <div class="kpi-card">
                <h3>Sem Resposta Humana</h3>
                <p>{sem_resposta} <span style="font-size:14px; font-weight:normal;">({pct_sem_resposta:.1f}%)</span></p>
                <small>Encerrados na fila/bot</small>
            </div>
            <div class="kpi-card">
                <h3>Ociosidade de Encerramento</h3>
                <p>{tempo_encerramento_formatado}</p>
                <small>Média até fechar o chat</small>
            </div>
        </div>

        <div class="highlight-box">
            ⏰ <strong>Distribuição Horária da Demanda:</strong> {texto_horarios}
        </div>

        <h2>📌 Detalhamento de Solução por Assunto</h2>
        <table>
            <thead>
                <tr>
                    <th>Assunto Principal</th>
                    <th>Total Demanda</th>
                    <th>Solucionados</th>
                    <th>Não Solucionados</th>
                    <th>Outros / Testes</th>
                    <th>% Resolução</th>
                </tr>
            </thead>
            <tbody>
                {matriz_assuntos_html}
            </tbody>
        </table>

        <h2>👥 Desempenho e Produtividade da Equipe</h2>
        <table>
            <thead>
                <tr>
                    <th>Atendente</th>
                    <th>Atendimentos Realizados</th>
                    <th>Demandas Solucionadas</th>
                    <th>Atendimentos c/ Áudio</th>
                    <th>Taxa de Resolução</th>
                </tr>
            </thead>
            <tbody>
                {desempenho_agentes if desempenho_agentes else "<tr><td colspan='5'>Sem dados disponíveis</td></tr>"}
            </tbody>
        </table>

        <div class="footer">
            Relatório gerado automaticamente pelo Sistema Inteligente de Análise de Atendimento do TRE-PB com anonimização total de PII conforme a LGPD.
        </div>
    </body>
    </html>
    """
    return html_content