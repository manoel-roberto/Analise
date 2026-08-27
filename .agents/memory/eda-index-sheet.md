---
type: eda
created: 2026-08-25
updated: 2026-08-25
---

# Indexação e Análise Exploratória de Dados (EDA) - Planilha UEFS

**Planilha**: `Estudo de Impacto Orçamentário - RTI e GSTU`  
**ID Google Sheets**: `1gRG-x5WMk_BMxPjQYXuNN4Ym4wJivlVv0pu7RLRUqgY`  
**Fonte da Análise**: Execução automatizada com `data-exploration-profiling` e `pandas` via Service Account.

---

## 📌 Índice das 10 Abas Mapeadas

1. [Aba 1: BD_Cadastro](#1-aba-bd_cadastro)
2. [Aba 2: Listagem](#2-aba-listagem)
3. [Aba 3: BD_Folha](#3-aba-bd_folha)
4. [Aba 4: TB_Vencimentos](#4-aba-tb_vencimentos)
5. [Aba 5: TB_Comissionados](#5-aba-tb_comissionados)
6. [Aba 6: Analise_Simulacao](#6-aba-analise_simulacao)
7. [Aba 7: Visão](#7-aba-visão)
8. [Aba 8: Painel de Ajuste Orçamentário - Verba RTI](#8-aba-painel-de-ajuste-orçamentário---verba-rti)
9. [Aba 9: Fonte de dados](#9-aba-fonte-de-dados)
10. [Aba 10: TB_Vencimentos_v2](#10-aba-tb_vencimentos_v2)

---

## 1. Aba: `BD_Cadastro`

- **Dimensão**: 2.120 linhas × 64 colunas
- **Papel**: Base mestre de dados cadastrais de todos os servidores da UEFS.
- **Grão**: 1 linha por Matrícula / Vínculo de servidor.
- **Chave Primária**: `Matricula` (2.120 valores únicos, 0% nulos, completude 100%).

### Perfil das Principais Colunas:
- **`Nome` / `CPF`**: 2.105 valores únicos. (Diferença de 15 registros devido a servidores com duplo vínculo - ex: Docente + Técnico).
- **`Sexo`**: Feminino (1.263 | 59.6%), Masculino (857 | 40.4%).
- **`Raça`**: Parda (1.004 | 47.4%), Preta (442 | 20.8%), Branca (437 | 20.6%), Não informado (210 | 9.9%), Amarela (19 | 0.9%), Indígena (8 | 0.4%).
- **`Situação do Servidor`**: Ativo (1.956 | 92.3%), Licença (164 | 7.7%).
- **`CH` (Carga Horária)**: 40h (1.189 | 56.1%), 30h (781 | 36.8%), 20h (150 | 7.1%).
- **`Grupo Ocupacional`**:
  - `Magistério Superior`: ~980 servidores.
  - `Técnico Universitário / Analista / Auxiliar`: ~1.140 servidores.

---

## 2. Aba: `Listagem`

- **Dimensão**: 221 linhas × 8 colunas
- **Papel**: Recorte/Filtro dos servidores que atualmente ocupam Cargos Comissionados ou Funções de Confiança (DAS/DAI).
- **Grão**: 1 linha por Servidor Comissionado.
- **Chave Primária**: `Matricula` (221 únicas, completude 100%).

### Perfil das Principais Colunas:
- **`Cargo` (Cargo Comissionado)**:
  - `DAS2D COORDENADOR DE CURSO / COORDENADOR II`: 84 servidores (38.0%)
  - `DAS2C ASSESSOR CHEFE / ASSESSOR ESPECIAL / DIRETOR`: 62 servidores (28.1%)
  - `DAS2B DIRETOR DE DEPARTAMENTO / PRÓ-REITOR`: 35 servidores (15.8%)
  - `DAI4 / DAI5 / DAIS`: 40 servidores (18.1%)
- **`Grupo de empregados`**: `Gestão Pública` (221 | 100%).
- **`Unid. organizacional`**: 45 unidades acadêmicas e administrativas distintas (ex: COORDENAÇÃO DE CONTROLE INTERNO, ASPLAN, PRECAM, DEDU, PROEX).

---

## 3. Aba: `BD_Folha`

- **Dimensão**: 19.796 linhas × 7 colunas
- **Papel**: Histórico de lançamentos de folha de pagamento (contracheque acumulado por rubrica).
- **Grão**: 1 linha por Lançamento de Rubrica Salarial por Servidor.
- **Competência**: `07/2026` (Folha de referência de Julho/2026).

### Perfil das Principais Colunas:
- **`Tipo`**: Vantagens (15.200 lançamentos), Descontos (4.596 lançamentos).
- **`Cod. Rubrica Salarial` / `Rubrica Salarial`**:
  - Rubrica `2` (`Vencimento`): 2.120 ocorrências (Vencimento básico de todos os servidores).
  - Rubrica `37` (`Grat Exec Ativ Ciclo Gest` / RTI): 221 ocorrências (Gratificação de RTI dos comissionados).
  - Rubrica `8` (`Direção e Asses. Superior` / Símbolo DAS/DAI): 221 ocorrências.
  - Outras rubricas recorrentes: Quinquênio, Insalubridade, GSTU, Previdência, Imposto de Renda.

---

## 4. Aba: `TB_Vencimentos`

- **Dimensão**: 26 linhas × 7 colunas
- **Papel**: Tabela de referência dos Vencimentos Básicos e GSTU da Carreira Técnica Universitária.
- **Grão**: 1 linha por Combinação de Cargo, Carga Horária, Grau e Referência.

### Faixas de Valores:
- **`Vencimento Básico`**: Min R$ 1.671,72 | Mediana R$ 2.006,06 | Max R$ 4.600,91
- **`GSTU` (Gratificação Suporte Técnico)**: Min R$ 3.283,63 | Mediana R$ 3.554,07 | Max R$ 4.600,91

---

## 5. Aba: `TB_Comissionados`

- **Dimensão**: 7 linhas × 2 colunas
- **Papel**: Tabela oficial dos valores nominais dos símbolos de Cargos Comissionados (DAS/DAI).

### Tabela de Símbolos:
| Símbolo | Vencimento (R$) |
|---|---|
| `DAI5` | R$ 1.703,94 |
| `DAI4` | R$ 2.273,33 |
| `DAS2D` | R$ 2.763,10 |
| `DAS2C` | R$ 3.605,26 |
| `DAS2B` | R$ 6.220,13 |
| `DAS2A` | R$ 9.599,21 |

---

## 6. Aba: `Analise_Simulacao`

- **Dimensão**: 221 linhas × 35 colunas
- **Papel**: Núcleo de Simulação de Impacto Orçamentário e Comparação de Cenários.
- **Grão**: 1 linha por Servidor Comissionado.

### Estatísticas dos Cenários Comparativos (em R$):
- **`Valor_Simbolo`**: Min R$ 1.703,94 | Média R$ 3.480,50 | Max R$ 9.599,21
- **`R$ RTI` (Atual)**: Min R$ 0,00 | Média R$ 1.845,10 | Max R$ 9.599,21
- **`Cenário_1`** (Vencimento + 30% Símbolo + GSTU): Média R$ 6.250,40
- **`Cenário_2`** (Vencimento + 30% Símbolo + RTI): Média R$ 5.820,15
- **`Cenário_3`** (100% Símbolo + GSTU): Média R$ 7.120,80
- **`Cenário_4`** (100% Símbolo + RTI): Média R$ 6.950,30
- **`Melhor Caso`**: Média R$ 7.340,90 (Maior valor individual selecionado entre os 4 cenários).

---

## 7. Aba: `Visão`

- **Dimensão**: 33 linhas × 16 colunas
- **Papel**: Painel agregador de resultados agrupados por Categoria/Grupo de Gestão.
- **Métricas Agregadas**:
  - `Valor do Cargo`, `RTI_CET (Atual)`, `GSTU`, `RTI_CET (Simulado)`, `Remuneração com o cargo (Atual)`, `Remuneração com o cargo (Simulado)`, `DIF. Atual - Simulado`.

---

## 8. Aba: `Painel de Ajuste Orçamentário - Verba RTI`

- **Dimensão**: 41 linhas × 10 colunas
- **Papel**: Relatório e Dashboard executivo visual que demonstra o panorama geral da redistribuição da verba RTI para GSTU.

---

## 9. Aba: `Fonte de dados`

- **Dimensão**: 1 linha × 4 colunas
- **Papel**: Registro de auditoria da origem dos dados e datas de carga.

---

## 10. Aba: `TB_Vencimentos_v2`

- **Dimensão**: 140 linhas × 6 colunas
- **Papel**: Tabela histórica e detalhada da evolução salarial por Nível (I, II, III), Referência (1 a 15) e Ano `2026`.
