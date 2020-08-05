"""
Executa a análise DEA separadamente em cada cluster e armazena o resultado em planilhas
individualizadas por cluster e em uma única planilha consolidada.
"""

import os

import pandas as pd

from pydea_wrapper import ModeloDEA
from consts import ANO, DIRETORIO_DADOS, DIRETORIO_RESULTADOS

if __name__ == '__main__':

    # Parâmetros do modelo do TCU
    input_categories = ['CNES_LEITOS_SUS', 'CNES_MEDICOS', 'CNES_PROFISSIONAIS_ENFERMAGEM', 'CNES_SALAS']
    output_categories = ['SIA_SIH_VALOR']
    virtual_weight_restrictions = ['CNES_LEITOS_SUS >= 0.16',
                                   'CNES_MEDICOS >= 0.16'
                                   'CNES_PROFISSIONAIS_ENFERMAGEM >= 0.09',
                                   'CNES_SALAS >= 0.09']

    # Instancia modelo DEA
    modelo_tcu = ModeloDEA(input_categories, output_categories, virtual_weight_restrictions)

    # Coleta path do arquivo "xlsx" de dados com a coluna de label do cluster
    arquivo_dados_dea = os.path.join(DIRETORIO_DADOS, 'hosp_pubs_{ANO}_clusterizado.xlsx'.format(ANO=ANO))

    # Lê o arquivo "xlsx" como um objeto pandas DataFrame
    df = pd.read_excel(arquivo_dados_dea)

    # Executa DEA
    modelo_tcu.executa_por_cluster(arquivo_dados_dea, DIRETORIO_RESULTADOS, 'CLUSTER')
