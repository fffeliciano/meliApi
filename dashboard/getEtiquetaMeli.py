import requests
import pandas as pd
import zipfile
import os
import shutil
import json


#1-----------------------------------------------------------------------------------------------------------

import requests

def download_zip(shipping_id, order_code, autorization):
    """
    Faz o download de um arquivo .zip a partir de uma API e salva-o localmente.
    
    :param api_url: URL base da API
    :param order_code: Código do pedido para buscar o arquivo .zip
    :param output_filename: Nome do arquivo para salvar o .zip
    """
    # outpu_filename
    output_filename = order_code + ".zip"

    # Montar a URL completa
    #url = f"{api_url}/{order_code}"
    url = f"https://api.mercadolibre.com/shipment_labels?shipment_ids={shipping_id}&response_type=zpl2"
    #print(url)
    #exit(99)

    #url = "https://api.mercadolibre.com/shipment_labels?shipment_ids=43450269387&response_type=zpl2"

    payload = {}
   
    headers = {'Authorization': f'Bearer {autorization}'}


    try:
        # Fazer a requisição GET para a API
        response = requests.get(url,headers=headers ,stream=True)

        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Abrir um arquivo local para escrita em modo binário
            with open(output_filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            print(f"Arquivo .zip salvo como {output_filename}")
        else:
            print(f"Erro ao fazer o download: {response.status_code}")
    except requests.RequestException as e:
        print(f"Erro na requisição: {e}")

# Uso da função
#api_url = "https://exemplo.com/api/download"
#order_code = "12345"
#output_filename = "pedido_12345.zip"

#1---------------------------------------------------------------------------------------------------------

#2 Descompactar--------------------------------------------------------------------------------------------
        

def extract_zip(zip_path, extract_to):
    """
    Descompacta o arquivo .zip na pasta especificada.
    
    :param zip_path: Caminho do arquivo .zip
    :param extract_to: Pasta onde o arquivo será descompactado
    """
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def process_files(extract_to, target_folder, new_txt_filename, new_zpl_filename):
    """
    Processa os arquivos descompactados, renomeando e movendo para a pasta de destino.
    
    :param extract_to: Pasta onde o arquivo foi descompactado
    :param target_folder: Pasta de destino para salvar os novos arquivos
    :param new_pdf_filename: Novo nome do arquivo PDF
    :param new_zpl_filename: Novo nome do arquivo ZPL
    """
    pdf_path = None
    zpl_path = None
    
    # Procurar arquivos PDF e ZPL na pasta descompactada
    #print("extract_to", extract_to )


    for root, dirs, files in os.walk(extract_to):
        #print("entrei no for!!!")
        #print("files , root ", files, root )

        for file in files:
            #print("file :", file)
            if file.endswith('.pdf'):
                #print("achei o pdf !")
                pdf_path = os.path.join(root, file)
            elif file.endswith('.txt'):
                #print("achei o txt !")
                zpl_path = os.path.join(root, file)
    
    # Verificar se os arquivos foram encontrados
    if not pdf_path or not zpl_path:
        raise FileNotFoundError("Arquivos .pdf e/ou .zpl não encontrados.")
    
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    
    # Renomear e mover arquivos para a pasta de destino
    #new_pdf_path = os.path.join(target_folder, new_pdf_filename)
    new_zpl_path = os.path.join(target_folder, new_zpl_filename)
    
    #shutil.move(pdf_path, new_pdf_path)
    shutil.move(zpl_path, new_zpl_path)
    
    #print(f"Arquivo PDF salvo como {new_pdf_path}")
    #print(f"Arquivo ZPL salvo como {new_zpl_path}")

    tamanho = get_file_size(new_zpl_path)
    #print(f"tamanho do arquivo {new_zpl_path}", tamanho)

    with open( f'etiquetas/{new_txt_filename}', 'w') as f:
        f.write(str(get_file_size(new_zpl_path)))


def descompactar(order_code, order_nf):
    #zip_path = 'caminho/do/seu/arquivo.zip'
    zip_path = f'{order_code}.zip'
    #extract_to = 'caminho/para/descompactar'
    extract_to = order_code
    #target_folder = 'caminho/para/salvar/novos/etiquetas'
    target_folder = 'etiquetas'
    #new_pdf_filename = f'{order_nf}.pdf'
    new_zpl_filename = f'{order_nf}.zpl'
    new_txt_filename = f'{order_nf}.txt'
    
    # Descompacta o arquivo .zip
    extract_zip(zip_path, extract_to)
    
    # Processa os arquivos descompactados e renomeia
    process_files(extract_to, target_folder, new_txt_filename, new_zpl_filename)
    
    # Limpeza opcional: remove a pasta descompactada
    shutil.rmtree(extract_to)

"""
if __name__ == '__main__':
    main()
"""




#2 Descompactar--------------------------------------------------------------------------------------------




#3 Tamanho do arquivo ZPL---------------------------------------------------------------------------------

# GERAR UMA ARQUIVO TXT CONTEUNDO O TAMANHO DO ARQUIVO ZPL.
#



# Método 1: Usando a função os.path.getsize


def get_file_size(file_path):
    return os.path.getsize(file_path)

#file_path = 'caminho/para/seu/arquivo.zpl'
#file_size = get_file_size(file_path)

#nrEtiqueta = input("Digite o numero da Nota Fiscal: ")
#with open( f'etiquetas/{nrEtiqueta}.txt', 'w') as f:
#    f.write("0")


#print(f"O tamanho do arquivo .zpl é: {file_size} bytes")


#3 Tamanho do arquivo ZPL---------------------------------------------------------------------------------




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

    dados1 = dados

    # Fazer um resumo dos dados usando as funcionalidades do Pandas
    #resumo = df.describe()
    #resumo = df.columns
    

    return df


# Vai buscar todos os pedidos com status 1 na API dos Pedidos da F3C
def buscar(token):

    # URL da API RESTful
    # url = 'https://meli.f3system.com.br/pedidos/pdd/'
    #  http://mbp.f3system.com.br/pedidos/pedidos/?status=1
    url = 'http://mbp.f3system.com.br/pedidos/pedidos/?status=1'

    # Token de autenticação
    

    # Fazer a solicitação paginada
    dados = fazer_request_paginada(url, token)

    # Verificar se os dados foram recuperados com sucesso
    if dados:
        # Fazer um resumo dos dados
        resumo = resumir_dados(dados)
        #print("resumo", resumo)
    else:
        print("Falha ao recuperar os dados da API.")

    return dados


#gettoken---------------------------------------------------------------------------------------------

def getToken(loja):

    # URL da API RESTful
    # url = 'https://meli.f3system.com.br/pedidos/pdd/'
    #  http://mbp.f3system.com.br/pedidos/pedidos/?status=1
    #url = 'http://mbp.f3system.com.br/pedidos/pedidos/?status=1'
    url = f'https://meli.f3system.com.br/access/access/{loja}'

    # Token de autenticação
    #  token = '3e695a9da0bbd634e561fafef17c16ccb3cb8139'
    token = '3e695a9da0bbd634e561fafef17c16ccb3cb8139'

    headers = {'Authorization': f'Token {token}'}

    # Fazer a solicitação paginada
        
    response = requests.get(url, headers=headers)

    # Verifique se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Converter os dados da resposta para formato JSON
        data = response.json()  
        return data['access_token']

    else:
        print("Falha ao recuperar os dados da API.")
        return None


#gettoken---------------------------------------------------------------------------------------------


#atualizar o status do pedido no Database MPB---------------------------------------------------------------


def update_pedido(numpedcli, token, dados):
    
    #Envia uma requisição POST para atualizar o pedido na API Django.
    
    #:param api_url: URL base da API
    #:param token: Token de acesso para autenticação
    #:param pedido_id: ID do pedido a ser atualizado
    #:param status: Novo status do pedido
    #:param tamanho_file_etiqueta: Novo tamanho do arquivo de etiqueta

    #'http://mbp.f3system.com.br/pedidos/pedidos/67367/'
    api_url = 'http://mbp.f3system.com.br/pedidos/pedidos'

    url = f"{api_url}/{numpedcli}/"

    
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    data = dados
    

    #print(url, data, headers)


    response = requests.put(url, json=data, headers=headers)

    #print(response.text)


    
    if response.status_code == 200:
        print("Pedido atualizado com sucesso.")
        print("Resposta da API:", response.json())
    else:
        print(f"Falha ao atualizar o pedido. Status code: {response.status_code}")
        print("Resposta da API:", response.json())

# Uso da função
#api_url = 'http://localhost:8000'  # Substitua pela URL correta da sua API
#token = 'seu_token_de_acesso'
#pedido_id = 1  # Substitua pelo ID do pedido que deseja atualizar
#status = 'processado'
#tamanho_file_etiqueta = get_file_size(file_path)

#update_pedido(api_url, token, pedido_id, status, tamanho_file_etiqueta)




#atualizar o status do pedido no Database MPB---------------------------------------------------------------

def pegarEtiquetaMeli(nrPedido):


    url = "https://api.mercadolibre.com/shipment_labels?shipment_ids=42701695664&response_type=zpl2"

    payload = {}
    headers = {
    'Authorization': 'Bearer APP_USR-4375699992396972-053116-bdf27bf1c06f7bd012642111f15badfc-82898594'
    }

    # https://meli.f3system.com.br/access/access/
    # APP_USR-4375699992396972-053116-bdf27bf1c06f7bd012642111f15badfc-82898594


    response = requests.request("GET", url, headers=headers, data=payload)

    #print(response.text)
    



def getIdOrder(order_code,autorization):
    #url = "https://api.mercadolibre.com/orders/2000008408097422"
    api_url = "https://api.mercadolibre.com/orders"
    url = url = f"{api_url}/{order_code}"
    acesso = f"Bearer {autorization}"
    payload = {}
    headers = {'Authorization': acesso}

    #print(" vamos pegar o id_shippin ", url, headers, payload )
    response = requests.request("GET", url, headers=headers, data=payload)
    #print("retorno de response", response.text)

    return response.text



# inicio
# Vai pegar o token para acessar os pedidos na API do ml 
loja = 2 # 1 idcom, 2 mbp
autorization = getToken(loja)
#print("getAuth :::",autorization)

##############################################################################################
# pegar todos os pedidos na API do mbp.f3system 
token = '29adb932a099ec021f34d767997154a18594974d'
##############################################################################################

ver = buscar(token)

#print(ver)

#print(ver[['loja', 'numpedrca', 'numnf']])

#print(type(ver))


#exit(99)
for n in ver:
    #order_code = ver['numpedrca'][10]
    order_code = n['numpedrca']
    order_nf = n['numnf']
    numpedcli = n['numpedcli']

    #print("numpedrca :::>>", ver['numpedrca'][10])
    if n['loja'] == 'MercadoLivre':
        json_str = getIdOrder(order_code, autorization)
        json1_data = json.loads(json_str)

        #print(json1_data['shipping']['id'])

        download_zip(json1_data['shipping']['id'], order_code, autorization)

        v1 = descompactar(order_code, order_nf)
        
        n['status'] = 6
        n['tamanhoEtiqueta'] = get_file_size(f'etiquetas/{order_nf}.zpl')
        dados=n
        
        #print(dados)
        #exit(88)
        v2 = update_pedido(numpedcli, token, dados)

        #print("fim do registro")
        exit(99)

    else:
        print("este pedido é da loja :", n['loja'])




