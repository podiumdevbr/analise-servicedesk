import pandas as pd
from datetime import datetime

def gerar_relatorio_html(df_filtrado, periodo_str="Período Geral"):
    """
    Gera uma estrutura HTML formatada como relatório executivo para impressão/download.
    """
    total_atendimentos = len(df_filtrado)
    resolvidos = len(df_filtrado[df_filtrado['status_solucao'] == 'Resolvido'])
    taxa_resolucao = (resolvidos / total_atendimentos * 100) if total_atendimentos > 0 else 0
    atendimentos_audio = int(df_filtrado['Tem_Audio'].sum()) if 'Tem_Audio' in df_filtrado.columns else 0
    sem_resposta = int((~df_filtrado['Resposto_Por_Agente']).sum()) if 'Resposto_Por_Agente' in df_filtrado.columns else 0

    # Top Assuntos
    top_assuntos = df_filtrado['assunto_principal'].value_counts().head(5).to_dict() if not df_filtrado.empty else {}
    
    # Avaliação de Cordialidade
    qualidade_dist = df_filtrado['qualidade_atendimento'].value_counts().to_dict() if not df_filtrado.empty else {}

    # Desempenho por Atendente
    desempenho_agentes = ""
    if not df_filtrado.empty and 'Agente' in df_filtrado.columns:
        agente_summary = df_filtrado.groupby('Agente').agg(
            Total=('Protocolo', 'count'),
            Resolvidos=('status_solucao', lambda x: (x == 'Resolvido').sum())
        ).reset_index()
        agente_summary['Taxa'] = (agente_summary['Resolvidos'] / agente_summary['Total'] * 100).round(1)
        
        for _, row in agente_summary.iterrows():
            desempenho_agentes += f"<tr><td>{row['Agente']}</td><td>{row['Total']}</td><td>{row['Resolvidos']}</td><td>{row['Taxa']}%</td></tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Relatório Executivo - Service Desk TRE-PB</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 30px; color: #333; }}
            h1 {{ color: #003366; border-bottom: 2px solid #003366; padding-bottom: 8px; }}
            h2 {{ color: #005599; margin-top: 25px; }}
            .kpi-container {{ display: flex; justify-content: space-between; margin: 20px 0; }}
            .kpi-card {{ background: #f4f7f9; border-left: 5px solid #005599; padding: 15px; width: 22%; box-sizing: border-box; }}
            .kpi-card h3 {{ margin: 0; font-size: 14px; color: #666; }}
            .kpi-card p {{ margin: 5px 0 0 0; font-size: 22px; font-weight: bold; color: #003366; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
            th {{ background-color: #003366; color: white; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .footer {{ margin-top: 40px; font-size: 12px; color: #777; text-align: center; border-top: 1px solid #ddd; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <h1>⚖️ Tribunal Regional Eleitoral da Paraíba - TRE-PB</h1>
        <h2>Relatório Executivo de Desempenho do Service Desk</h2>
        <p><strong>Período Analisado:</strong> {periodo_str} | <strong>Data da Emissão:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        
        <div class="kpi-container">
            <div class="kpi-card"><h3>Total Atendimentos</h3><p>{total_atendimentos}</p></div>
            <div class="kpi-card"><h3>Taxa de Resolução</h3><p>{taxa_resolucao:.1f}%</p></div>
            <div class="kpi-card"><h3>Com Áudio</h3><p>{atendimentos_audio}</p></div>
            <div class="kpi-card"><h3>Sem Resposta Humana</h3><p>{sem_resposta}</p></div>
        </div>

        <h2>📌 Top Demanda de Assuntos</h2>
        <table>
            <tr><th>Assunto Principal</th><th>Quantidade</th></tr>
            {"".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in top_assuntos.items()])}
        </table>

        <h2>⚖️ Qualidade e Cordialidade do Atendimento</h2>
        <table>
            <tr><th>Avaliação</th><th>Quantidade</th></tr>
            {"".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in qualidade_dist.items()])}
        </table>

        <h2>👥 Produtividade por Atendente</h2>
        <table>
            <tr><th>Atendente</th><th>Atendimentos</th><th>Resolvidos</th><th>Taxa de Resolução</th></tr>
            {desempenho_agentes if desempenho_agentes else "<tr><td colspan='4'>Sem dados disponíveis</td></tr>"}
        </table>

        <div class="footer">
            Relatório gerado automaticamente pelo Sistema de Análise de Atendimento do TRE-PB com anonimização conforme a LGPD.
        </div>
    </body>
    </html>
    """
    return html_content