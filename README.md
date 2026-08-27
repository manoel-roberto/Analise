# 🏛️ Sistema Automático de Atualização DW → Google Sheets (UEFS)

Aplicação profissional de ETL, Auditoria Pré-Importação e Sincronização Automática entre os relatórios exportados do DW da Universidade Estadual de Feira de Santana (UEFS) e a planilha de **Estudo de Impacto Orçamentário (RTI e GSTU)** no Google Sheets.

---

## 🌟 Funcionalidades Principais

1. **🌐 Interface Web Interativa (Streamlit Dashboard)**:
   - Carregamento / Upload visual dos arquivos do DW (`bd-MM.YYYY.xls` e `folha-MM.YYYY.xls`).
   - Painel com KPIs (Servidores, Ingressos, Exonerações, Mudanças de Função/Símbolo, Variação Salarial).
   - Abas interativas de pré-visualização das auditorias antes de gravar.
   - **Botão de Ação "Atualizar Banco de Dados no Google Sheets Agora"**.

2. **📊 Auditoria Pré-Importação Completa nos 8 Domínios de RH**:
   - 🟢 **Ingressos / Novos Servidores**: Mapeia todas as novas admissões.
   - 🔴 **Desligamentos / Ausentes**: Mapeia servidores exonerados ou ausentes da folha.
   - 🎭 **Função Comissionada & Símbolo**: Nomeações e exonerações de DAS/DAI.
   - 🎓 **Cargo & Carreira**: Alterações de cargo, classe e jornada.
   - 📍 **Lotação & Setor**: Remanejamentos entre unidades e departamentos.
   - 💰 **Variação Salarial**: Proventos, Vantagens e Descontos.

3. **🔒 Preservação Total da Planilha Oficial**:
   - Atualiza exclusivamente as tabelas fontes (`BD_Cadastro` e `BD_Folha`).
   - Preserva todas as 8 abas de análises dinâmicas, tabelas dinâmicas e fórmulas originais (`TB_Vencimentos`, `TB_Comissionados`, `TB_Vencimentos_v2`, etc.).

---

## 🚀 Como Executar

### 1. Iniciar a Interface Visual Web (Recomendado):
```bash
.venv/bin/streamlit run app.py
```
Acesse no seu navegador: `http://localhost:8501`

### 2. Executar via Linha de Comando (CLI):
```bash
# Somente auditoria pré-importação (sem alterar o Google Sheets)
.venv/bin/python main.py report

# Atualização efetiva no Google Sheets
.venv/bin/python main.py update
```

---

## 📂 Arquivos Gerados Automaticamente:

- [`relatorio_auditoria_completa_mudancas_rh.csv`](file:///home/manoel/projetos/Analise/relatorio_auditoria_completa_mudancas_rh.csv): Planilha CSV detalhada de todas as alterações.
- [`relatorio_auditoria_completa_mudancas_rh.md`](file:///home/manoel/projetos/Analise/relatorio_auditoria_completa_mudancas_rh.md): Relatório executivo em Markdown.
