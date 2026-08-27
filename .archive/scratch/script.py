import gspread

# 1. Autenticar usando o arquivo JSON de Conta de Serviço
cliente = gspread.service_account(filename='acaua-web-4898dee734cb.json')

# 3. Acessar a planilha e a aba específica
planilha = cliente.open('Estudo de Impacto Orçamentário - RTI e GSTU')
aba = planilha.worksheet('BD_Cadastro')

# 4. Operações de Banco de Dados (CRUD)
# LER: Puxar todos os registros (retorna uma lista de dicionários)
dados = aba.get_all_records()
print(dados)

# INSERIR: Adicionar uma nova linha de dados
#aba.append_row(['Valor Coluna 1', 'Valor Coluna 2', 'Valor Coluna 3'])

# ATUALIZAR: Atualizar a célula B2
#aba.update('B2', 'Novo Valor')