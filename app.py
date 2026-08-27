import streamlit as st
import pandas as pd
import os
import sys

# Garante inclusão da raiz do projeto no PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.config import CREDENTIALS_FILE, SPREADSHEET_ID, DEFAULT_IMPORT_DIR, TAB_BD_CADASTRO, TAB_BD_FOLHA
from src.ingestion.dw_parser import find_latest_dw_files, parse_dw_cadastro, parse_dw_folha
from src.transformation.cadastro_processor import process_cadastro_for_sheets
from src.transformation.folha_processor import process_folha_for_sheets
from src.sheets.google_sheets_client import GoogleSheetsConnector
from src.reports.change_mapper import run_comprehensive_change_audit, format_comprehensive_audit_markdown
from src.reports.pdf_generator import generate_audit_pdf_bytes

st.set_page_config(
    page_title="Gestor DW → Google Sheets | UEFS",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada Premium
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        font-size: 1.1rem;
        height: 3rem;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #1D4ED8;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🏛️ Painel de Atualização Automática DW → Google Sheets</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Estudo de Impacto Orçamentário (RTI / GSTU) - Universidade Estadual de Feira de Santana</div>', unsafe_allow_html=True)

# Sidebar
try:
    st.sidebar.image("https://www.uefs.br/wp-content/themes/uefs/assets/img/logo-uefs.png", width=180)
except Exception:
    st.sidebar.markdown("### 🏛️ UEFS")

st.sidebar.title("⚙️ Controle & Origem de Dados")

# Status da Conexão com Google Sheets
@st.cache_resource(show_spinner="Conectando ao Google Sheets...")
def get_sheets_connector():
    try:
        connector = GoogleSheetsConnector(CREDENTIALS_FILE, SPREADSHEET_ID)
        connector.connect()
        return connector, True, "Conectado ao Google Sheets"
    except Exception as e:
        return None, False, str(e)

connector, connected, status_msg = get_sheets_connector()

if connected:
    st.sidebar.success(f"🟢 **Google Sheets Conectado**\n\n`Cópia de Estudo de Impacto Orçamentário`")
else:
    st.sidebar.error(f"🔴 **Erro de Conexão**: {status_msg}")

st.sidebar.markdown("---")

# Opções de Seleção ou Upload de Arquivos do DW
st.sidebar.subheader("📂 Arquivos do DW")

dw_source = st.sidebar.radio("Selecione a fonte dos arquivos:", ["Pasta `import/` do sistema", "Fazer Upload de Novos Arquivos"])

bd_file_path = None
folha_file_path = None

if dw_source == "Pasta `import/` do sistema":
    try:
        bd_file_path, folha_file_path = find_latest_dw_files(DEFAULT_IMPORT_DIR)
        st.sidebar.info(f"📄 **Cadastro**: `{os.path.basename(bd_file_path)}`")
        st.sidebar.info(f"📄 **Folha**: `{os.path.basename(folha_file_path)}`")
    except Exception as e:
        st.sidebar.error(f"Arquivos não encontrados em {DEFAULT_IMPORT_DIR}")

else:
    uploaded_bd = st.sidebar.file_uploader("Upload Cadastro DW (`bd-*.xls`)", type=["xls", "xlsx", "csv"])
    uploaded_folha = st.sidebar.file_uploader("Upload Folha DW (`folha-*.xls`)", type=["xls", "xlsx", "csv"])
    
    if uploaded_bd and uploaded_folha:
        os.makedirs("import_temp", exist_ok=True)
        bd_file_path = os.path.join("import_temp", uploaded_bd.name)
        folha_file_path = os.path.join("import_temp", uploaded_folha.name)
        with open(bd_file_path, "wb") as f: f.write(uploaded_bd.getbuffer())
        with open(folha_file_path, "wb") as f: f.write(uploaded_folha.getbuffer())
        st.sidebar.success("Arquivos carregados com sucesso!")

# Execução do Processamento e Auditoria
if bd_file_path and folha_file_path and connected:
    
    @st.cache_data(show_spinner="Carregando e auditando alterações do DW...")
    def load_and_audit(bd_path, folha_path):
        df_cad_orig = connector.get_worksheet_dataframe(TAB_BD_CADASTRO)
        df_folha_orig = connector.get_worksheet_dataframe(TAB_BD_FOLHA)
        
        df_raw_cad = parse_dw_cadastro(bd_path)
        df_raw_folha = parse_dw_folha(folha_path)
        
        df_cad_novo = process_cadastro_for_sheets(df_raw_cad, df_existing_bd=df_cad_orig)
        df_folha_novo = process_folha_for_sheets(df_raw_folha)
        
        audit_results = run_comprehensive_change_audit(
            df_cad_orig=df_cad_orig,
            df_raw_dw_cad=df_raw_cad,
            df_folha_orig=df_folha_orig,
            df_folha_novo=df_folha_novo
        )
        return df_cad_orig, df_folha_orig, df_cad_novo, df_folha_novo, audit_results

    df_cad_orig, df_folha_orig, df_cad_novo, df_folha_novo, audit_results = load_and_audit(bd_file_path, folha_file_path)

    # Cards KPI Superiores
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Servidores Base", f"{audit_results['total_servidores']:,}")
    with col2:
        st.metric("🟢 Ingressos", f"{audit_results['novos_count']}", delta="Novos Servidores")
    with col3:
        st.metric("🔴 Exonerações / Saídas", f"{audit_results['saidas_count']}", delta="-Saídas", delta_color="inverse")
    with col4:
        st.metric("🎭 Função / Símbolo", f"{audit_results['domain_summary'].get('Função Comissionada & Símbolo', 0)}")
    with col5:
        st.metric("💰 Total de Ocorrências", f"{audit_results['total_alteracoes']:,}")

    st.markdown("---")

    # Botão de Ação Destacado: Gravar Atualizações
    st.subheader("🚀 Ação: Gravação no Google Sheets")
    st.warning("⚠️ **Atenção**: Esta ação substituirá automaticamente as abas `BD_Cadastro` e `BD_Folha` na planilha oficial do Google Sheets, mantendo intactas todas as fórmulas e gráficos das abas dinâmicas.")
    
    if st.button("⚡ ATUALIZAR BANCO DE DADOS NO GOOGLE SHEETS AGORA"):
        with st.spinner("Gravando atualizações no Google Sheets... Por favor, aguarde."):
            try:
                updates = {
                    TAB_BD_CADASTRO: df_cad_novo,
                    TAB_BD_FOLHA: df_folha_novo
                }
                connector.update_batch(updates)
                st.balloons()
                st.success("✅ **SUCESSO!** As abas `BD_Cadastro` e `BD_Folha` foram atualizadas com sucesso no Google Sheets!")
            except Exception as e:
                st.error(f"❌ Erro ao atualizar planilha: {str(e)}")

    st.markdown("---")

    # Visualização das Tabelas do Relatório de Auditoria
    st.subheader("📋 Relatório Prévio de Auditoria de Mudanças")
    
    tabs = st.tabs([
        "🟢 Ingressos (Novos Servidores)",
        "🔴 Exonerações / Ausentes",
        "🎭 Função & Símbolo / Cargo",
        "💰 Variação na Folha",
        "📑 Relatório Completo (PDF / CSV / MD)"
    ])

    df_diffs = pd.DataFrame(audit_results['diff_records'])

    # Tab 1: Ingressos
    with tabs[0]:
        st.write(f"### 🟢 Novos Servidores Admitidos ({audit_results['novos_count']})")
        df_ing = df_diffs[df_diffs['Domínio RH'] == 'Ingressos / Novos Servidores']
        if not df_ing.empty:
            st.dataframe(df_ing[['Matricula', 'Nome', 'Status / Observação']], use_container_width=True)
        else:
            st.info("Nenhum novo servidor admitido nesta carga.")

    # Tab 2: Desligamentos
    with tabs[1]:
        st.write(f"### 🔴 Servidores Ausentes / Exonerados ({audit_results['saidas_count']})")
        df_saidas = df_diffs[df_diffs['Domínio RH'] == 'Desligamentos / Ausentes']
        if not df_saidas.empty:
            st.dataframe(df_saidas[['Matricula', 'Nome', 'Status / Observação']], use_container_width=True)
        else:
            st.info("Nenhum servidor exonerado/ausente nesta carga.")

    # Tab 3: Função e Símbolo
    with tabs[2]:
        st.write("### 🎭 Mudanças de Função Comissionada, Símbolo ou Cargo")
        df_func = df_diffs[df_diffs['Domínio RH'].isin(['Função Comissionada & Símbolo', 'Cargo & Carreira'])]
        if not df_func.empty:
            st.dataframe(df_func[['Matricula', 'Nome', 'Campo Alterado', 'Valor Anterior (Base)', 'Valor Novo (DW)']], use_container_width=True)
        else:
            st.info("Nenhuma mudança de função ou símbolo encontrada.")

    # Tab 4: Folha
    with tabs[3]:
        st.write("### 💰 Variação na Folha de Pagamento por Servidor")
        df_folha_diff = df_diffs[df_diffs['Domínio RH'] == 'Folha de Pagamento - Proventos']
        if not df_folha_diff.empty:
            st.dataframe(df_folha_diff[['Matricula', 'Nome', 'Valor Anterior (Base)', 'Valor Novo (DW)', 'Status / Observação']], use_container_width=True)
        else:
            st.info("Sem alterações financeiras salariais.")

    # Tab 5: Exportar Relatórios (PDF, CSV e MD)
    with tabs[4]:
        st.write("### 📑 Download dos Relatórios de Auditoria")
        st.info("Selecione o formato desejado para baixar o relatório completo da carga:")

        col_pdf, col_csv, col_md = st.columns(3)

        with col_pdf:
            pdf_bytes = generate_audit_pdf_bytes(audit_results)
            st.download_button(
                label="📕 Baixar Relatório Executivo em PDF",
                data=pdf_bytes,
                file_name="relatorio_auditoria_dw_uefs.pdf",
                mime="application/pdf"
            )

        with col_csv:
            csv_bytes = df_diffs.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📊 Baixar Tabela Completa em CSV (Excel)",
                data=csv_bytes,
                file_name="relatorio_auditoria_dw_uefs.csv",
                mime="text/csv"
            )

        with col_md:
            md_text = format_comprehensive_audit_markdown(audit_results)
            st.download_button(
                label="📝 Baixar Documento em Markdown (.md)",
                data=md_text.encode('utf-8'),
                file_name="relatorio_auditoria_dw_uefs.md",
                mime="text/markdown"
            )

else:
    st.info("Aguardando carregamento de arquivos do DW e conexão com o Google Sheets...")
