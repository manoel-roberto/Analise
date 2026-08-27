import os
import io
import pandas as pd
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_audit_pdf_bytes(audit_data: Dict[str, Any]) -> bytes:
    """
    Gera um relatório executivo em PDF formatado (bytes) para download direto via Streamlit.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Estilos customizados
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=6,
        alignment=0
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=15
    )

    heading2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=colors.HexColor('#1E3A8A'),
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1F2937')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1F2937')
    )

    elements = []

    # Cabeçalho
    elements.append(Paragraph("🏛️ UEFS - Universidade Estadual de Feira de Santana", title_style))
    elements.append(Paragraph("Relatório Executivo de Auditoria de Mudanças (DW vs Google Sheets)", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=15))

    # Resumo Executivo
    elements.append(Paragraph("📌 Resumo Executivo da Carga de Dados", heading2_style))

    summary_table_data = [
        [
            Paragraph("<b>Métrica / Indicador</b>", table_header_style),
            Paragraph("<b>Quantidade / Valor</b>", table_header_style),
            Paragraph("<b>Status da Auditoria</b>", table_header_style)
        ],
        [
            Paragraph("Servidores na Base Anterior (07/2026)", table_cell_style),
            Paragraph(f"<b>{audit_data['total_servidores']:,}</b>", table_cell_style),
            Paragraph("Base Atualizada", table_cell_style)
        ],
        [
            Paragraph("Servidores na Nova Carga DW (08/2026)", table_cell_style),
            Paragraph(f"<b>{audit_data['total_dw']:,}</b>", table_cell_style),
            Paragraph("Processado", table_cell_style)
        ],
        [
            Paragraph("🟢 Ingressos (Novos Servidores)", table_cell_style),
            Paragraph(f"<b>{audit_data['novos_count']}</b>", table_cell_style),
            Paragraph("Novas Admissões", table_cell_style)
        ],
        [
            Paragraph("🔴 Desligamentos (Exonerações/Ausentes)", table_cell_style),
            Paragraph(f"<b>{audit_data['saidas_count']}</b>", table_cell_style),
            Paragraph("Saídas Mapeadas", table_cell_style)
        ],
        [
            Paragraph("🎭 Função Comissionada & Símbolo", table_cell_style),
            Paragraph(f"<b>{audit_data['domain_summary'].get('Função Comissionada & Símbolo', 0)}</b>", table_cell_style),
            Paragraph("Alterações de DAS/DAI", table_cell_style)
        ],
        [
            Paragraph("💰 Total de Ocorrências Mapeadas", table_cell_style),
            Paragraph(f"<b>{audit_data['total_alteracoes']:,}</b>", table_cell_style),
            Paragraph("Auditado com Sucesso", table_cell_style)
        ],
    ]

    t_summary = Table(summary_table_data, colWidths=[230, 140, 150])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#9CA3AF')),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F9FAFB')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#ECFDF5')),
        ('BACKGROUND', (0, 4), (-1, 4), colors.HexColor('#FEF2F2')),
    ]))
    elements.append(t_summary)
    elements.append(Spacer(1, 15))

    df_rec = pd.DataFrame(audit_data['diff_records'])

    # 1. Ingressos
    if not df_rec.empty:
        df_ing = df_rec[df_rec['Domínio RH'] == 'Ingressos / Novos Servidores']
        if not df_ing.empty:
            elements.append(Paragraph(f"🟢 Ingressos - Novos Servidores Admitidos ({len(df_ing)})", heading2_style))
            ing_data = [[
                Paragraph("<b>Matrícula</b>", table_header_style),
                Paragraph("<b>Nome do Servidor</b>", table_header_style),
                Paragraph("<b>Cargo / Setor / Observação</b>", table_header_style)
            ]]
            for _, r in df_ing.head(20).iterrows():
                ing_data.append([
                    Paragraph(str(r['Matricula']), table_cell_style),
                    Paragraph(str(r['Nome']), table_cell_style),
                    Paragraph(str(r['Status / Observação']), table_cell_style)
                ])
            t_ing = Table(ing_data, colWidths=[80, 220, 220])
            t_ing.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#A7F3D0')),
            ]))
            elements.append(t_ing)
            elements.append(Spacer(1, 15))

        # 2. Desligamentos
        df_saidas = df_rec[df_rec['Domínio RH'] == 'Desligamentos / Ausentes']
        if not df_saidas.empty:
            elements.append(Paragraph(f"🔴 Desligamentos - Servidores Ausentes / Exonerados ({len(df_saidas)})", heading2_style))
            saida_data = [[
                Paragraph("<b>Matrícula</b>", table_header_style),
                Paragraph("<b>Nome do Servidor</b>", table_header_style),
                Paragraph("<b>Cargo / Setor Anterior</b>", table_header_style)
            ]]
            for _, r in df_saidas.head(20).iterrows():
                saida_data.append([
                    Paragraph(str(r['Matricula']), table_cell_style),
                    Paragraph(str(r['Nome']), table_cell_style),
                    Paragraph(str(r['Status / Observação']), table_cell_style)
                ])
            t_saida = Table(saida_data, colWidths=[80, 220, 220])
            t_saida.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#FECACA')),
            ]))
            elements.append(t_saida)
            elements.append(Spacer(1, 15))

        # 3. Função & Símbolo
        df_func = df_rec[df_rec['Domínio RH'].isin(['Função Comissionada & Símbolo', 'Cargo & Carreira'])]
        if not df_func.empty:
            elements.append(Paragraph(f"🎭 Mudanças de Função Comissionada, Símbolo ou Cargo ({len(df_func)})", heading2_style))
            func_data = [[
                Paragraph("<b>Matrícula</b>", table_header_style),
                Paragraph("<b>Nome</b>", table_header_style),
                Paragraph("<b>Cargo Anterior</b>", table_header_style),
                Paragraph("<b>Cargo Novo (DW)</b>", table_header_style)
            ]]
            for _, r in df_func.iterrows():
                func_data.append([
                    Paragraph(str(r['Matricula']), table_cell_style),
                    Paragraph(str(r['Nome']), table_cell_style),
                    Paragraph(str(r['Valor Anterior (Base)']), table_cell_style),
                    Paragraph(str(r['Valor Novo (DW)']), table_cell_style)
                ])
            t_func = Table(func_data, colWidths=[70, 160, 145, 145])
            t_func.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#C7D2FE')),
            ]))
            elements.append(t_func)
            elements.append(Spacer(1, 15))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
