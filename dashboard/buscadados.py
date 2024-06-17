import requests
import pandas as pd
import json

def fazer_request_paginada(url, token):
    dados_completos = []
    proxima_pagina = url

    # Define o cabeçalho de autorização com o token
    headers = {'Authorization': f'Token {token}'}

    # Continue fazendo solicitações até não haver mais páginas
    while proxima_pagina:
        response = requests.get(proxima_pagina, headers=headers)

        # Verifique se a solicitação foi bem-sucedida
        if response.status_code == 200:
            # Converter os dados da resposta para formato JSON
            data = response.json()

            # Adicione os dados da página atual à lista de dados completos
            dados_completos.extend(data['results'])

            # Verifique se há uma próxima página
            proxima_pagina = data['next']
        else:
            print("Falha ao recuperar os dados da API.")
            return None

    return dados_completos

def salvar_cache_dados(dados, arquivo_cache):
    with open(arquivo_cache, 'w') as f:
        json.dump(dados, f)

def carregar_cache_dados(arquivo_cache):
    with open(arquivo_cache, 'r') as f:
        dados = json.load(f)
    return dados

def carregar_dados():
    return pd.read_json(arquivo_cache)

def carregar_cache_category(arquivo_cache_category):
    with open(arquivo_cache_category, 'r', encoding='utf8') as f:
        category = json.load(f)
    return category


# Carregar dados
#------------------------------------------------------------------
# URL da API RESTful
#url = 'https://meli.f3system.com.br/pedidos/pdd/'
url = 'https://meli.f3system.com.br/pedidos/pedidos/'

# Token de autenticação
token = '3e695a9da0bbd634e561fafef17c16ccb3cb8139'

# Fazer a solicitação paginada

# Nome do arquivo de cache
arquivo_cache = 'dados_cache.json'
arquivo_cache_category = '../meliApi1/category.json'

#arquivo_cache = 'dados_cache_1.json'
#arquivo_cache_category = '../meliApi1/category_1.json'

try:
    dados = carregar_cache_dados(arquivo_cache)
    category=carregar_cache_category(arquivo_cache_category)
    print("Dados carregados do cache.")
except FileNotFoundError:
    # Se o cache não existir, fazer uma solicitação para a API
    print("Fazendo solicitação à API...")
    dados = fazer_request_paginada(url, token)
    if dados:
        # Salvar dados em cache
        salvar_cache_dados(dados, arquivo_cache)
#------------------------------------------------------------------

dados = carregar_dados()

#dados = fazer_request_paginada(url, token)











