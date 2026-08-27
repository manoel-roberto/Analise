import sys
import os
import argparse
import logging
from pathlib import Path

from src.config import (
    CREDENTIALS_FILE, SPREADSHEET_ID, DEFAULT_IMPORT_DIR,
    TAB_BD_CADASTRO, TAB_BD_FOLHA
)
from src.ingestion.dw_parser import find_latest_dw_files, parse_dw_cadastro, parse_dw_folha
from src.transformation.cadastro_processor import process_cadastro_for_sheets
from src.transformation.folha_processor import process_folha_for_sheets
from src.sheets.google_sheets_client import GoogleSheetsConnector
from src.reports.change_reporter import generate_pre_import_audit_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DW_Sheet_Updater")

def run_pipeline(import_dir: str, dry_run: bool = False, generate_report_only: bool = False):
    logger.info("=== PIPELINE DW → GOOGLE SHEETS COM AUDITORIA PRÉ-IMPORTAÇÃO AUTOMÁTICA ===")
    
    # 1. Localiza arquivos DW
    bd_file, folha_file = find_latest_dw_files(import_dir)
    if not bd_file or not folha_file:
        logger.error("Arquivos do DW não encontrados na pasta import.")
        sys.exit(1)
        
    logger.info(f"Arquivo Cadastro DW: {bd_file}")
    logger.info(f"Arquivo Folha DW:    {folha_file}")
    
    # 2. Conexão com Google Sheets
    connector = GoogleSheetsConnector(CREDENTIALS_FILE, SPREADSHEET_ID)
    connector.connect()
    
    # Carrega dados atuais do Google Sheets (Linha de base do mês anterior)
    logger.info("Carregando base atual do Google Sheets para comparação...")
    df_cad_orig = connector.get_worksheet_dataframe(TAB_BD_CADASTRO)
    df_folha_orig = connector.get_worksheet_dataframe(TAB_BD_FOLHA)
    
    # 3. Parsing e Processamento dos dados novos do DW
    logger.info("Executando parsing e normalização dos dados novos do DW...")
    df_raw_cad = parse_dw_cadastro(bd_file)
    df_raw_folha = parse_dw_folha(folha_file)
    
    df_cad_novo = process_cadastro_for_sheets(df_raw_cad, df_existing_bd=df_cad_orig)
    df_folha_novo = process_folha_for_sheets(df_raw_folha)
    
    # 4. GERAÇÃO AUTOMÁTICA DO RELATÓRIO PRÉ-IMPORTAÇÃO DE MUDANÇAS
    md_path = os.path.join(import_dir, "..", "relatorio_mudancas_pre_importacao.md")
    csv_path = os.path.join(import_dir, "..", "relatorio_mudancas_pre_importacao.csv")
    
    audit_data = generate_pre_import_audit_report(
        df_cad_orig=df_cad_orig,
        df_cad_novo=df_cad_novo,
        df_folha_orig=df_folha_orig,
        df_folha_novo=df_folha_novo,
        output_md_path=md_path,
        output_csv_path=csv_path
    )
    
    logger.info(f"📄 RELATÓRIO PRÉ-IMPORTAÇÃO GERADO COM SUCESSO:")
    logger.info(f"  - Markdown: {os.path.abspath(md_path)}")
    logger.info(f"  - CSV:      {os.path.abspath(csv_path)}")
    
    print("\n" + "=" * 80)
    print(audit_data['md_content'])
    print("=" * 80 + "\n")
    
    if generate_report_only or dry_run:
        logger.info("🔍 MODO SIMULAÇÃO / RELATÓRIO: Nenhuma alteração foi gravada online no Google Sheets.")
        return

    # 5. Gravação Efetiva no Google Sheets (BD_Cadastro e BD_Folha)
    logger.info("🚀 ENVIANDO ATUALIZAÇÕES PARA AS TABELAS FONTES NO GOOGLE SHEETS...")
    updates = {
        TAB_BD_CADASTRO: df_cad_novo,
        TAB_BD_FOLHA: df_folha_novo
    }
    connector.update_batch(updates)
    logger.info("✅ PLANILHA DO GOOGLE SHEETS ATUALIZADA COM SUCESSO! Relatório pré-importação gravado.")

def main():
    parser = argparse.ArgumentParser(description="Sistema de Atualização com Auditoria Pré-Importação Automática (DW → Google Sheets)")
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")
    
    # update
    up = subparsers.add_parser("update", help="Executa a auditoria pré-importação e atualiza BD_Cadastro e BD_Folha no Google Sheets")
    up.add_argument("--import-dir", default=DEFAULT_IMPORT_DIR)
    
    # dry-run
    dr = subparsers.add_parser("dry-run", help="Gera o relatório pré-importação em modo de simulação (sem alterar o Google Sheets)")
    dr.add_argument("--import-dir", default=DEFAULT_IMPORT_DIR)
    
    # report
    rp = subparsers.add_parser("report", help="Gera exclusivamente o relatório pré-importação em Markdown e CSV")
    rp.add_argument("--import-dir", default=DEFAULT_IMPORT_DIR)
    
    # status
    subparsers.add_parser("status", help="Verifica a conexão com o Google Sheets")

    args = parser.parse_args()

    if args.command == "update":
        run_pipeline(args.import_dir, dry_run=False)
    elif args.command == "dry-run":
        run_pipeline(args.import_dir, dry_run=True)
    elif args.command == "report":
        run_pipeline(args.import_dir, generate_report_only=True)
    elif args.command == "status":
        connector = GoogleSheetsConnector(CREDENTIALS_FILE, SPREADSHEET_ID)
        connector.connect()
        logger.info("Conexão OK!")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
