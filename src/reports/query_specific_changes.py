import pandas as pd

df = pd.read_csv('relatorio_alteracoes_por_servidor.csv')

# Filtra Mudança de Função / Símbolo (5 alterações)
df_funcao = df[df['Categoria da Mudança'] == 'Mudança de Função / Símbolo']

# Filtra Alteração Cadastral (4 alterações)
df_cadastral = df[df['Categoria da Mudança'] == 'Alteração Cadastral']

print("=== MUDANÇA DE FUNÇÃO / SÍMBOLO (5 ALTERAÇÕES) ===")
for idx, r in df_funcao.iterrows():
    print(f"Matrícula: {r['Matricula']} | Nome: {r['Nome']}")
    print(f"  Campo: {r['Campo Alterado']}")
    print(f"  Anterior (07/2026): {r['Valor Anterior (07/2026)']}")
    print(f"  Novo (08/2026):     {r['Valor Novo (08/2026)']}")
    print("-" * 50)

print("\n=== ALTERAÇÃO CADASTRAL (4 ALTERAÇÕES) ===")
for idx, r in df_cadastral.iterrows():
    print(f"Matrícula: {r['Matricula']} | Nome: {r['Nome']}")
    print(f"  Campo: {r['Campo Alterado']}")
    print(f"  Anterior (07/2026): {r['Valor Anterior (07/2026)']}")
    print(f"  Novo (08/2026):     {r['Valor Novo (08/2026)']}")
    print("-" * 50)
