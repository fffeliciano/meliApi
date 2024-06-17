import requests
import pandas as pd
import plotly.express as px
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

def resumir_dados(dados):
    # Criar DataFrame Pandas com os dados
    df = pd.DataFrame(dados)

    # Fazer um resumo dos dados usando as funcionalidades do Pandas
    #resumo = df.describe()
    #resumo = df.columns
    

    return df


def buscar():

    # URL da API RESTful
    url = 'https://meli.f3system.com.br/pedidos/pdd/'

    # Token de autenticação
    token = '3e695a9da0bbd634e561fafef17c16ccb3cb8139'

    # Fazer a solicitação paginada
    dados = fazer_request_paginada(url, token)

    # Verificar se os dados foram recuperados com sucesso
    if dados:
        # Fazer um resumo dos dados
        resumo = resumir_dados(dados)
        #print(resumo)
    else:
        print("Falha ao recuperar os dados da API.")

    return resumo


