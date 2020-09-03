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

import pandas as pd
import numpy as np

import xlsxwriter
import openpyxl

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


def trata_dados_para_dea(df_mes, df_cluster):

    # Insere a coluna REGIAO antes da coluna UF em "df_mes" usando o objeto dict "UF_REGIAO"
    insere_coluna_antes_em_df(df_mes, consts.UF_REGIAO, 'UF', 'UF', 'REGIAO')

    # Insere a coluna ESFERA_FEDERATIVA antes da coluna TIPO_UNIDADE em "df_mes" usando o objeto...
    # dict "NATJUR_ESFERA"
    insere_coluna_antes_em_df(df_mes, consts.NATJUR_ESFERA, 'NAT_JURIDICA', 'TIPO_UNIDADE', 'ESFERA_FEDERATIVA')

    # Insere a coluna TIPO_ADMIN_PUB antes da coluna TIPO_UNIDADE em "df_mes" usando o objeto dict...
    # "NATJUR_TIPO_ADMIN_PUB"
    insere_coluna_antes_em_df(df_mes, consts.NATJUR_TIPO_ADMIN_PUB, 'NAT_JURIDICA', 'TIPO_UNIDADE', 'TIPO_ADMIN_PUB')

    # Coleta o index do elemento 'NAT_JURIDICA' pertencente ao objeto list "df_mes.columns.to_list()"
    pos_coluna_nat_jur = df_mes.columns.to_list().index('NAT_JURIDICA')
    # Aplica a função "retorna_faixa_leitos" a cada elemento da coluna CNES_LEITOS_SUS de "df_mes"
    faixa_leitos = df_mes['CNES_LEITOS_SUS'].apply(retorna_faixa_leitos)
    # Insere em "df_mes" a coluna FAIXA_LEITOS antes da coluna NAT_JURIDICA tendo os valores...
    # contidos em "faixa_leitos"
    df_mes.insert(loc=pos_coluna_nat_jur, column='FAIXA_LEITOS', value=faixa_leitos)

    # Coleta o index do elemento 'NAT_JURIDICA' pertencente ao objeto list "df_mes.columns.to_list()"...
    # e acresce o inteiro 1
    pos_col_depois_nat_jur = df_mes.columns.to_list().index('NAT_JURIDICA') + 1
    # Cria objeto list dos valores do objeto dict map_nat_jur chamados pelas chaves k e...
    # contidos no primento elemento do objeto string que constitui a coluna NAT_JURIDICA...
    # de "df_mes"
    nat_jur_simplificada = [consts.MAP_NAT_JUR[k] for k in df_mes['NAT_JURIDICA'].str[0]]
    # Insere em "df_mes" a coluna NAT_JURIDICA_SIMPLIFICADA depois da coluna NAT_JURIDICA tendo...
    # os valores contidos em "nat_jur_simplificada"
    df_mes.insert(loc=pos_col_depois_nat_jur, column='NAT_JURIDICA_SIMPLIFICADA', value=nat_jur_simplificada)

    print('Início:', df_mes.shape)

    # Mantém somente unidades de caráter hospitalar
    df_hosp = df_mes[df_mes['TIPO_UNIDADE'].isin(consts.TIPOS_UNIDADES_MANTIDAS)]

    print('Após remover não-hospitais:', df_hosp.shape)

    # Remove unidades não públicas
    df_hosp_pubs = df_hosp[df_hosp['NAT_JURIDICA_SIMPLIFICADA'] == 'ADMINISTRAÇÂO PÚBLICA']

    print('Após remover entidades não públicas:', df_hosp_pubs.shape)

    # Coleta PATH do arquivo "lista_ibross.xlsx"
    arquivo_lista_ibross = os.path.join(consts.DIRETORIO_DADOS, 'lista_ibross.xlsx')
    # Lê o arquivo "lista_ibross.xlsx" como um objeto pandas DataFrame e transforma a...
    # coluna CNES em um objeto list dos códigos CNES contidos na coluna CNES
    lista_cnes_oss = pd.read_excel(arquivo_lista_ibross)['CNES'].to_list()

    # Coleta o index do elemento 'TIPO_UNIDADE' pertencente ao objeto list "df_hosp_pubs.columns.to_list()"
    pos_col_apos_tipo_unidade = df_hosp_pubs.columns.to_list().index('TIPO_UNIDADE')
    # Cria objeto list de elementos "SIM" ou "NA" conforme estão em "lista_cnes_oss" ou não
    se_gerida_oss = ['SIM' if cnes in lista_cnes_oss else 'NA' for cnes in df_hosp_pubs['CNES']]
    # Insere em "df_tudo" a coluna SE_GERIDA_OSS antes da coluna TIPO tendo os valores...
    # contidos em "se_gerida_oss"
    df_hosp_pubs.insert(loc=pos_col_apos_tipo_unidade, column='SE_GERIDA_OSS', value=se_gerida_oss)

    # Mantém em "df_hosp_pubs" somente os hospitais públicos presentes em "df_cluster"
    df_hosp_pubs = df_hosp_pubs[df_hosp_pubs['CNES'].isin(df_cluster['CNES'].to_list())]

    # Reseta o index de "df_hosp_pubs"
    df_hosp_pubs.reset_index(drop=True, inplace=True)

    # Merge "df_cluster" e "df_hosp_pubs"
    df_hosp_pubs = pd.merge(df_cluster, df_hosp_pubs, how='inner', left_on='CNES', right_on='CNES')

    return df_hosp_pubs


def prepara_dados_range(first_period='01-2017', last_period='12-2019'):

    first_year = int(first_period[3:])
    last_year = int(last_period[3:])

    last_month = last_period[:2]

    df_cluster = pd.read_excel(os.path.join(consts.DIRETORIO_DADOS, f'dados_clusterizados_{first_year}_a_{last_year}.xlsx'))

    # Itera sobre os anos
    for ano in np.arange(first_year, last_year + 1):

        if ano == last_year:

            # Itera sobre os meses do último ano de dados
            for mes in np.arange(1, int(last_month) + 1):

                # Converte o tipo int referenciado à variável "mes" como tipo string
                mes = str(mes)

                # Preenche com zeros à esquerda a string "mes" até ficar com dois dígitos
                mes = mes.zfill(2)
                
                print('\n********************************')
                print(f'{ano}-{mes}')

                # Lê o arquivo xlsx "dados_para_dea_'year'_'month'" como um objeto pandas DataFrame
                df_mes = pd.read_excel(os.path.join(consts.DIRETORIO_DADOS, f'dados_para_dea_{ano}_{mes}.xlsx'))

                df_hosp_pubs = trata_dados_para_dea(df_mes, df_cluster)

                df_hosp_pubs.to_excel(os.path.join(consts.DIRETORIO_DADOS, f'dados_tratados_dea_{ano}_{mes}.xlsx'), index=False)

        else:

            # Itera sobre os meses do período
            for mes in np.arange(1, 13):

                mes = str(mes)
                mes = mes.zfill(2)
                print('\n********************************')
                print(f'{ano}-{mes}')

                # Lê o arquivo xlsx "dados_para_dea_'year'_'month'" como um objeto pandas DataFrame
                df_mes = pd.read_excel(os.path.join(consts.DIRETORIO_DADOS, f'dados_para_dea_{ano}_{mes}.xlsx'))

                df_hosp_pubs = trata_dados_para_dea(df_mes, df_cluster)

                df_hosp_pubs.to_excel(os.path.join(consts.DIRETORIO_DADOS, f'dados_tratados_dea_{ano}_{mes}.xlsx'), index=False)



if __name__ == '__main__':

    prepara_dados_range('01-2017', '12-2019')
