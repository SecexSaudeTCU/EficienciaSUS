"""
Prepara planilhas para clusterização e análise DEA.
    Origem dos dados:
     - Os valores de produção registrados no SIA e no SIH foram obtidos pela soma de todos os meses do respectivo ano
     - As demais variáveis e a lista de hospitais (i.e. lista de ids do CNES) foram obtidas do mês de dez de cada ano

    Exclusão e inclusão de unidades (valores de 2018):
     - Unidades não hospitalares são removidas (sobram 7.745 de um total original de 331.058)
     - Unidades não públicas são removidas (sobram 3.304)
     - Unidades com valor zero em variável utilizada pela DEA (sobram 2.861 de 3.304)
"""

import os
from zipfile import ZipFile

import pandas as pd

import consts



def insere_coluna_antes_em_df(frame, dicionario, coluna_base, coluna_posicao, coluna_nova):
    """
    Insere a coluna coluna_nova antes da coluna coluna_posicao do objeto pandas DataFrame
    frame cujos valores pertencem ao objeto dict dicionario e foram obtidas através da
    iteração sobre as chaves do objeto dict dicionario que constituem a coluna coluna_base
    do objeto pandas DataFrame frame
    """

    # Cria objeto list dos valores do objeto dict dicionario chamados pelas chaves key e...
    # contidos na coluna coluna_base do objeto pandas DataFrame frame
    list_valores = [dicionario[key] for key in frame[coluna_base]]

    # Coleta o index do elemento coluna_posicao pertencente ao objeto list...
    # "frame.columns.to_list()"
    index_coluna_posicao = frame.columns.to_list().index(coluna_posicao)

    # Insere no objeto pandas DataFrame "frame" a coluna coluna_nova antes da coluna...
    # coluna_posicao tendo os valores contidos em "list_valores"
    frame.insert(loc=index_coluna_posicao, column=coluna_nova, value=list_valores)


def retorna_faixa_leitos(num_leitos):
    """
    Retorna um valor 'categórico' de faixa de valor dependendo do valor inteiro
    num_leitos
    """
    if num_leitos < 1: return 'NA'
    elif num_leitos < 26: return '1 a 25'
    elif num_leitos < 51: return '26 a 50'
    elif num_leitos < 201: return '51 a 200'
    elif num_leitos < 301: return '201 a 300'
    return 'Mais de 300'



if __name__ == '__main__':

    # Coleta path da pasta de dados em formato zip (que contém um único arquivo "csv")
    arquivo_dados_zip = os.path.join(consts.DIRETORIO_DADOS, 'd{ANO}.zip'.format(ANO=consts.ANO))

    # Inicializa objeto da class ZipFile valendo-se da variável "arquivo_dados_zip"
    zip = ZipFile(arquivo_dados_zip, 'r')

    # Cria string do nome do arquivo de dados
    arquivo_dados = 'd{ANO}.csv'.format(ANO=consts.ANO)

    # Utiliza o método "extract" da class ZipFile para extrair o arquivo de nome "arquivo_dados"
    zip.extract(arquivo_dados)

    # Lê o arquivo de nome "arquivo_dados" como um objeto pandas DataFrame
    df_tudo = pd.read_csv(arquivo_dados)

    # Deleta arquivo de nome "arquivo_dados"
    os.unlink(arquivo_dados)

    # Insere a coluna REGIAO antes da coluna UF em "df_tudo" usando o objeto dict "UF_REGIAO"
    insere_coluna_antes_em_df(df_tudo, consts.UF_REGIAO, 'UF', 'UF', 'REGIAO')

    # Insere a coluna ESFERA_FEDERATIVA antes da coluna TIPO em "df_tudo" usando o objeto...
    # dict "NATJUR_ESFERA"
    insere_coluna_antes_em_df(df_tudo, consts.NATJUR_ESFERA, 'NAT_JURIDICA', 'TIPO', 'ESFERA_FEDERATIVA')

    # Insere a coluna TIPO_ADMIN_PUB antes da coluna TIPO em "df_tudo" usando o objeto dict...
    # "NATJUR_TIPO_ADMIN_PUB"
    insere_coluna_antes_em_df(df_tudo, consts.NATJUR_TIPO_ADMIN_PUB, 'NAT_JURIDICA', 'TIPO', 'TIPO_ADMIN_PUB')

    # Coleta o index do elemento 'NAT_JURIDICA' pertencente ao objeto list "df_tudo.columns.to_list()"
    pos_coluna_nat_jur = df_tudo.columns.to_list().index('NAT_JURIDICA')
    # Aplica a função "retorna_faixa_leitos" a cada elemento da coluna CNES_LEITOS_SUS de "df_tudo"
    faixa_leitos = df_tudo['CNES_LEITOS_SUS'].apply(retorna_faixa_leitos)
    # Insere em "df_tudo" a coluna FAIXA_LEITOS antes da coluna NAT_JURIDICA tendo os valores...
    # contidos em "faixa_leitos"
    df_tudo.insert(loc=pos_coluna_nat_jur, column='FAIXA_LEITOS', value=faixa_leitos)

    # Substiui NaN pelo valor zero nos valores da produção do SIA e do SIH, respectivamente
    df_tudo['VALOR_SIA'].fillna(value=0, inplace=True)
    df_tudo['VALOR_SIH'].fillna(value=0, inplace=True)

    # Coleta o index do elemento 'NAT_JURIDICA' pertencente ao objeto list "df_tudo.columns.to_list()"...
    # e acresce o inteiro 1
    pos_col_depois_nat_jur = 1 + df_tudo.columns.to_list().index('NAT_JURIDICA')
    # Cria objeto list dos valores do objeto dict map_nat_jur chamados pelas chaves k e...
    # contidos no primento elemento do objeto string que constitui a coluna NAT_JURIDICA...
    # de "df_tudo"
    nat_jur_siplificada = [consts.MAP_NAT_JUR[k] for k in df_tudo['NAT_JURIDICA'].str[0]]
    # Insere em "df_tudo" a coluna NAT_JURIDICA_SIMPLIFICADA depois da coluna NAT_JURIDICA tendo...
    # os valores contidos em "nat_jur_simplificada"
    df_tudo.insert(loc=pos_col_depois_nat_jur, column='NAT_JURIDICA_SIMPLIFICADA', value=nat_jur_siplificada)

    print('\n********************************\n')
    print('Início:', df_tudo.shape)

    # Mantém somente unidades de caráter hospitalar
    df_hosp = df_tudo[df_tudo['TIPO'].isin(consts.TIPOS_UNIDADES_MANTIDAS)]

    print('Após remover não-hospitais:', df_hosp.shape)

    # Remove unidades não públicas
    df_hosp_pubs = df_hosp[df_hosp['NAT_JURIDICA_SIMPLIFICADA'] == 'Administração Pública']

    print('Após remover entidades não públicas:', df_hosp_pubs.shape)

    # Coleta PATH do arquivo "lista_ibross.xlsx"
    arquivo_lista_ibross = os.path.join(consts.DIRETORIO_DADOS, 'lista_ibross.xlsx')
    # Lê o arquivo "lista_ibross.xlsx" como um objeto pandas DataFrame e transforma a...
    # coluna CNES em um objeto list dos códigos CNES contidos na coluna CNES
    lista_cnes_oss = pd.read_excel(arquivo_lista_ibross)['CNES'].to_list()

    # Coleta o index do elemento 'TIPO' pertencente ao objeto list "df_tudo.columns.to_list()"
    pos_col_apos_tipo_unidade = df_hosp_pubs.columns.to_list().index('TIPO')
    # Cria objeto list de elementos "SIM" ou "NA" conforme estão em "lista_cnes_oss" ou não
    se_gerida_oss = ['SIM' if cnes in lista_cnes_oss else 'NA' for cnes in df_hosp_pubs['CNES_ID']]
    # Insere em "df_tudo" a coluna SE_GERIDA_OSS antes da coluna TIPO tendo os valores...
    # contidos em "se_gerida_oss"
    df_hosp_pubs.insert(loc=pos_col_apos_tipo_unidade, column='SE_GERIDA_OSS', value=se_gerida_oss)

    # Coleta o index do elemento 'VALOR_SIA' pertencente ao objeto list "df_tudo.columns.to_list()"
    pos_col_valor_sia = df_hosp_pubs.columns.to_list().index('VALOR_SIA')
    # Cria objeto pandas Series que é a soma das colunas VALOR_SIA e VALOR_SIH de "df_tudo"
    valor_total = df_hosp_pubs['VALOR_SIA'] + df_hosp_pubs['VALOR_SIH']
    # Insere em "df_tudo" a coluna SIA_SIH_VALOR antes da coluna VALOR_SIA tendo os valores...
    # contidos em "valor_total"
    df_hosp_pubs.insert(loc=pos_col_valor_sia, column='SIA_SIH_VALOR', value=valor_total)

    # Renomeia as colunas mencionadas
    df_hosp_pubs = df_hosp_pubs.rename(columns={'CNES_ID': 'CNES',
                                                'MUNNOME': 'MUNICIPIO',
                                                'ATIVIDADE': 'ATIVIDADE_ENSINO',
                                                'TIPO': 'TIPO_UNIDADE'})

    # Remove as colunas mencionadas
    df_hosp_pubs = df_hosp_pubs.drop(columns=['GESTAO',  # Talvez esta coluna seja interessante para comparar OSS gerida por Estado x Municio
                                              'PRESTADOR',
                                              'VALOR_SIA',
                                              'VALOR_SIH',
                                              'QTD_SIA',
                                              'QTD_SIH'])

    print('Removendo linhas com valor zero nas colunas utilizadas para DEA...')

    # Desconsidera hospitais que possuem valor igual a zero para alguma das variáveis utilizadas na DEA
    for coluna in consts.COLUNAS_DEA:
        mascara = df_hosp_pubs[coluna] == 0
        df_hosp_pubs = df_hosp_pubs[~mascara]
        print(' * {n} linhas revmovidas por conter zero na coluna {coluna}'.format(n=sum(mascara), coluna=coluna))
    print('Número de estabelecimentos ao final do processamento: {n}'.format(n=df_hosp_pubs.shape[0]))

    # Coleta o PATH do arquivo "xlsx" a salvar
    arquivo_para_dea = os.path.join(consts.DIRETORIO_DADOS, 'hosp_pubs_{ANO}.xlsx'.format(ANO=consts.ANO))
    # Salva o objeto pandas DataFrame "df_hosp_pubs" como um arquivo "xlsx"
    df_hosp_pubs.to_excel(arquivo_para_dea, index=False)
