---
type: domain
created: 2026-08-25
updated: 2026-08-25
---

# Análise Exploratória e Comparativa dos Arquivos do DW (08/2026)

**Arquivos Analisados (Pasta `import/`)**:
1. `bd-.08.2026.xls` (51,19 MB) — Exportação de Cadastro de Servidores do DW.
2. `folha-08.2026.xls` (16,13 MB) — Exportação da Folha de Pagamento do DW.

**Formato Físico**: MHTML / MIME encapsulation com tabelas HTML codificadas em `quoted-printable` (quopri).

---

## 1. Perfil dos Arquivos Baixados do DW (Agosto/2026)

### A. Cadastro de Servidores (`bd-.08.2026.xls`)
- **Tabela Principal**: 13.206 linhas × 57 colunas.
- **Servidores Únicos (`Pessoa` / Matrícula)**: 2.061 matrículas ativas.
- **CPFs Únicos**: 2.045 CPFs.
- **Campos Principais Extraídos**:
  - `CPF`, `Pessoa` (Matrícula), `Nome`, `Sexo`, `Data de Admissão`, `Aniversário`, `Idade em anos`, `Vínculo empregatício`, `Status de ocupação`, `Tipo de Cargo`, `Cargo`, `Cargo Amplo`, `Cargo Efetivo`, `Cargo Origem`, `Nível salarial Efetivo`, `Área de RH`, `Subárea de RH`, `Símbolo do Cargo`, `Grupo de empregados`, `Grupo Ocupacional`, `Último Tipo de Medida`, `Raça`.

### B. Folha de Pagamento (`folha-08.2026.xls`)
- **Tabela Principal**: 25.741 lançamentos de rubricas × 8 colunas.
- **Competência**: `08.2026` (Folha de Agosto/2026).
- **Matrículas em Folha**: 2.121 servidores ativos com contracheque em 08/2026.
- **Totais Financeiros de 08/2026**:
  - **Vantagens Totais**: **R$ 25.265.311,06**
  - **Descontos Totais**: **R$ -9.950.638,90**
- **Servidores Comissionados com RTI em 08/2026**: 221 servidores ativos (Rubrica 37 e 8).

---

## 2. Comparativo: DW 08/2026 vs Planilha Google Atual (07/2026)

| Dimensão | Planilha Google (07/2026) | Arquivo DW (08/2026) | Impacto para Automação |
|---|---|---|---|
| **Competência** | 07/2026 | 08/2026 | Atualização mensal da base de cálculo e lançamentos. |
| **Linhas em BD_Folha** | 19.797 | 25.741 | +5.944 lançamentos atualizados a serem injetados em `BD_Folha`. |
| **Comissionados Ativos** | 222 | 221 | 1 movimentação/exoneração de cargo comissionado identificada. |

---

## 3. Diretrizes para a Aplicação de Atualização Automática

1. **Parser de Ingestão**: Usar decodificador `quopri` + parser HTML `lxml` para ler nativamente os arquivos `.xls` do DW.
2. **Mapeamento de Matrícula**: Chave primária universal = `Matrícula` (`Pessoa`).
3. **Sobregravação Segura**:
   - Atualizar a aba `BD_Cadastro` com os 2.061 servidores do DW.
   - Atualizar a aba `BD_Folha` com os 25.741 lançamentos de 08/2026.
   - Reprocessar a aba `Analise_Simulacao` garantindo a preservação dos percentuais dos 6 Grupos de Gestão e o recálculo dos 4 Cenários Comparativos.
