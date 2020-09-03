"""
Executa a análise DEA separadamente em cada cluster e armazena o resultado em planilhas
individualizadas por cluster e em uma única planilha consolidada.
"""

import os

import pandas as pd
import numpy as np
import xlsxwriter
import openpyxl

from pydea_wrapper import ModeloDEA
import consts



# Parâmetros do modelo do TCU
input_categories = consts.COLUNAS_DEA[:4]
output_categories = consts.COLUNAS_DEA[4:]
virtual_weight_restrictions = ['CNES_LEITOS_SUS >= 0.16',
                               'CNES_SALAS >= 0.09',
                               'CNES_MEDICOS >= 0.16',
                               'CNES_PROFISSIONAIS_ENFERMAGEM >= 0.09']


def executa_dea():

    # Instancia modelo DEA
    modelo_tcu = ModeloDEA(input_categories, output_categories, virtual_weight_restrictions)

    # Coleta path do arquivo "xlsx" de dados com a coluna de label do cluster
    arquivo_dados_dea = os.path.join(consts.DIRETORIO_DADOS, 'hosp_pubs_{ANO}_clusterizado.xlsx'.format(ANO=consts.ANO))

    # Lê o arquivo "xlsx" como um objeto pandas DataFrame
    df = pd.read_excel(arquivo_dados_dea)

    # Executa DEA
    modelo_tcu.executa_por_cluster(arquivo_dados_dea, consts.DIRETORIO_RESULTADOS, 'CLUSTER')


def executa_deas(first_period='01-2017', last_period='12-2019'):

    # Tenta abrir arquivo xlsx "resultados" caso exista
    try:

        workbook = openpyxl.load_workbook(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'))

        workbook.save(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'))

    # Cria arquivo xlsx "resultados" caso não exista
    except:

        workbook = xlsxwriter.Workbook(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'))

        workbook.close()

    # Coleta a substring referente ao ano e a transforma no tipo int
    first_year = int(first_period[3:])

    # Coleta a substring referente ao ano e a transforma no tipo int
    last_year = int(last_period[3:])

    # Coleta a substring do mês
    last_month = last_period[:2]

    # Itera sobre os anos
    for ano in np.arange(first_year, last_year + 1):

        if ano == last_year:

            # Itera sobre os meses do último ano de dados
            for mes in np.arange(1, int(last_month) + 1):

                # Converte o tipo int referenciado à variável "mes" como tipo string
                mes = str(mes)

                # Preenche com zeros à esquerda a string "mes" até ficar com dois dígitos
                mes = mes.zfill(2)

                # Instancia modelo DEA
                modelo_tcu = ModeloDEA(input_categories, output_categories, virtual_weight_restrictions)

                # Coleta path do arquivo xlsx "dados_tratados_dea_'ano'_'mes'"
                arquivo_dados_dea = os.path.join(consts.DIRETORIO_DADOS, 'dados_tratados_dea_{}_{}.xlsx'.format(ano, mes))

                # Executa DEA
                modelo_tcu.executa_por_cluster(arquivo_dados_dea, consts.DIRETORIO_RESULTADOS, 'CLUSTER')

                # Deleta o arquivo xlsx "dados_tratados_dea_'ano'_'mes'""
                os.unlink(arquivo_dados_dea)

                # Abre o arquivo xlsx de nome resultados
                workbook = openpyxl.load_workbook(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'))

                # Cria um objeto ExcelWriter para escrever no arquivo xlsx "resultados"
                writer = pd.ExcelWriter(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'), engine='openpyxl')

                # Vincula o objeto "workbook" ao atributo "book" de "writer"
                writer.book = workbook

                # Lê o arquivo xlsx "resultado_dados_tratados_dea_'ano'_'mes'"" como um objeto pandas DataFrame
                df = pd.read_excel(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultado_dados_tratados_dea_{}_{}.xlsx'.format(ano, mes)))

                # Coloca os dados de parte das colunas de "df" na planilha 'ano'-'mes' do arquivo xlsx "resultados"
                df[consts.COLUNAS_CATEGORICAS + ['EFICIENCIA']].to_excel(writer, sheet_name='{}-{}'.format(ano, mes), index=False)

                # Salva os dados
                writer.save()

                # Fecha o arquivo xlsx
                writer.close()

        else:

            # Itera sobre os meses de todos os anos menos do último
            for mes in np.arange(1, 13):

                mes = str(mes)
                mes = mes.zfill(2)

                # Instancia modelo DEA
                modelo_tcu = ModeloDEA(input_categories, output_categories, virtual_weight_restrictions)

                # Coleta path do arquivo xlsx "dados_tratados_dea_'ano'_'mes'"
                arquivo_dados_dea = os.path.join(consts.DIRETORIO_DADOS, 'dados_tratados_dea_{}_{}.xlsx'.format(ano, mes))

                # Executa DEA
                modelo_tcu.executa_por_cluster(arquivo_dados_dea, consts.DIRETORIO_RESULTADOS, 'CLUSTER')

                # Deleta o arquivo xlsx "dados_tratados_dea_'ano'_'mes'"
                os.unlink(arquivo_dados_dea)

                # Abre o arquivo xlsx "resultados"
                workbook = openpyxl.load_workbook(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'))

                # Cria um objeto ExcelWriter para escrever no arquivo xlsx "resultados"
                writer = pd.ExcelWriter(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'), engine='openpyxl')

                # Vincula o objeto "workbook" ao atributo "book" de "writer"
                writer.book = workbook

                # Lê o arquivo xlsx "resultado_dados_tratados_dea_'ano'_'mes'" como um objeto pandas DataFrame
                df = pd.read_excel(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultado_dados_tratados_dea_{}_{}.xlsx'.format(ano, mes)))

                # Colocaos dados de parte das colunas de "df" na planilha 'ano'-'mes' do arquivo xlsx resultados
                df[consts.COLUNAS_CATEGORICAS + ['EFICIENCIA']].to_excel(writer, sheet_name='{}-{}'.format(ano, mes), index=False)

                # Salva os dados
                writer.save()

                # Fecha o arquivo xlsx
                writer.close()

    # Abre o arquivo xlsx "resultados"
    workbook = openpyxl.load_workbook(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'))

    # Acessa o atributo "sheetnames" de "workbook"
    sheets_names = workbook.sheetnames

    # Deleta a planilha de nome "Sheet1"
    workbook.remove(workbook.get_sheet_by_name('Sheet1'))

    # Salva os dados
    workbook.save(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'))



if __name__ == '__main__':

    executa_deas('01-2017', '12-2019')
