---
type: domain
created: 2026-08-25
updated: 2026-08-25
---

# Mapeamento do Estudo de Impacto Orçamentário (RTI e GSTU) - UEFS

## 1. Visão Geral da Base de Dados
- **Spreadsheet Title**: `Estudo de Impacto Orçamentário - RTI e GSTU`
- **Spreadsheet ID**: `1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY`
- **Credencial de Acesso**: Service Account `acaua-web-4898dee734cb.json`
- **Contexto**: Estudo de impacto orçamentário relativo ao pagamento de Gratificações (RTI - Regime de Tempo Integral / CET e GSTU - Gratificação de Suporte Técnico Universitário) para servidores em cargos comissionados/funções na Universidade Estadual de Feira de Santana (UEFS).

---

## 2. Estrutura Completa das Abas (Worksheets)

| Aba | ID | Linhas Aprox. | Função Principal no Estudo |
|---|---|---|---|
| `BD_Cadastro` | `0` | 2.121 | **Base Mestre de Servidores**: Dados cadastrais completos (Matrícula, Nome, CPF, Admissão, Cargo Efetivo, Cargo Origem, Unidade Organizacional/Setor, Carga Horária, Grau). |
| `Listagem` | `598343767` | 222 | **Filtro dos Comissionados**: Recorte contendo os 222 servidores que ocupam Cargos Comissionados (DAS/DAI). |
| `BD_Folha` | `511452042` | 19.797 | **Histórico de Rubricas Salariais**: Extrato completo de lançamentos de vantagens e vencimentos (Rubricas 2, 8, 37, etc.) por competência. |
| `TB_Vencimentos` | `1605792815` | 27 | **Tabela de Vencimentos Universitários**: Valores de Vencimento Básico e GSTU por Cargo, Carga Horária e Grau (G1, G2...). |
| `TB_Comissionados` | `1065312138` | 8 | **Tabela de Símbolos Comissionados**: Valores nominais dos cargos DAS/DAI (DAI4, DAI5, DAS2A, DAS2B, DAS2C, DAS2D). |
| `Analise_Simulacao` | `1972252834` | 222 | **Motor de Simulação Orçamentária**: Cruzamento completo por servidor contendo valores atuais, acréscimos por Grupo e comparação de 4 Cenários. |
| `Visão` | `1121626289` | 34 | **Resumo Gerencial por Grupos**: Consolidação executiva por grupo de servidores (Acadêmicos, Gestores, Assessores). |
| `Painel de Ajuste Orçamentário - Verba RTI` | `552400499` | 41 | **Dashboard Visual**: Apresentação executiva dos valores atuais vs simulados. |
| `Fonte de dados` | `2049758721` | 1 | **Metadados de Origem**: Registros de datas de carga e manipulação. |
| `TB_Vencimentos_v2` | `151348115` | 141 | **Tabela de Vencimentos Expandida**: Histórico por Ano (ex: 2026) e referências salariais. |

---

## 3. Funcionamento da Automação Atual (`Código.js` / Apps Script)

- **ID do Script (`.clasp.json`)**: `1OIN6NzFEzOTAGVfjsybbcUnddrApj2_A9fsDUjYD4jAHDtjTNpdz-Tij`
- **Gatilho de Interface (`onOpen`)**: Adiciona menu `⚙️ Simulação RTI` > `Configurar Acréscimos Múltiplos`.
- **Painel HTML (`abrirPainelRTI`)**: Permite que o usuário insira percentuais de acréscimo para 6 Grupos:
  1. `1. Acadêmicos (Diretor)`
  2. `2. ADM (Gestor Acadêmico)`
  3. `3. ADM (Gestor ADM)`
  4. `4. Assessor em ascensão`
  5. `5. Assessores`
  6. `6. Funções Comissionadas`
- **Regra de Base de Cálculo (BC)** (`obterBaseCalculo`):
  - Exceção: Se Cargo == "Técnico Específico" => `BC = Valor do Símbolo (Coluna O)`.
  - Se `DAS/DAI (Coluna Q)` == `Valor Símbolo (Coluna O)` => `BC = DAS/DAI`.
  - Se `DAS/DAI` != `Valor Símbolo` => `BC = Vencimento Básico (Coluna P)`.
- **Cálculo de Simulação**:
  - `Novo % RTI (Coluna X)` = `% RTI Atual (Coluna T)` + `Acréscimo do Grupo`.
  - `Novo Valor R$ (Coluna Y)` = `BC` * `Novo % RTI`.
- **Gatilho Dinâmico (`onEdit`)**: Ao editar manualmente a Coluna X (% RTI) ou Y (Valor R$), recalcula a outra coluna bilateralmente com base na BC.

---

## 4. Requisitos Identificados para o Mecanismo de Atualização Automática

1. **Chave Primária de Rastreamento**: `Matrícula` (unifica cadastro, folha de pagamento e simulação).
2. **Eventos de Alteração Cadastral a Automatizar**:
   - Promoção / Mudança de Grau (afeta `TB_Vencimentos`).
   - Alteração de Cargo Comissionado / Símbolo (afeta `TB_Comissionados` e Grupo).
   - Transferência de Setor / Unidade Organizacional (preserva histórico e atualiza alocação).
3. **Preservação dos Cenários de Simulação**: O mecanismo de atualização deve atualizar a base de dados subjacente (`BD_Cadastro`, `BD_Folha`) e reprocessar os valores das abas `Analise_Simulacao` e `Visão` mantendo intactos os parâmetros de simulação previamente aplicados.
