"""
Executa a análise DEA separadaemente em cada cluster e armazena o resultado em planilhas indivudalizadas por cluster
e em um única planilha consolidada.
"""

import os
import pandas as pd
from pydea_wrapper import ModeloDEA
from consts import DIRETORIO_DADOS_INTERMEDIARIOS, DIRETORIO_DADOS_RESULTADOS

if __name__ == '__main__':

    #
    ANO = 2018

    # Parâmetros do modelo do TCU
    input_categories = ['CNES_LEITOS_SUS', 'CNES_MEDICOS', 'CNES_PROFISSIONAIS_ENFERMAGEM', 'CNES_SALAS']
    output_categories = ['SIA_SIH_VALOR']
    virtual_weight_restrictions = ['CNES_SALAS >= 0.09', 'CNES_PROFISSIONAIS_ENFERMAGEM >= 0.09',
                                   'CNES_LEITOS_SUS >= 0.16', 'CNES_MEDICOS >= 0.16']

    # Instancia modelo
    modelo_tcu = ModeloDEA(input_categories, output_categories, virtual_weight_restrictions)

    # Carrega planilha para DEA
    arquivo_dados_dea = os.path.join(DIRETORIO_DADOS_INTERMEDIARIOS,
                                     'hosp_pubs_{ANO}_clusterizado.xlsx'.format(ANO=ANO))
    # arquivo_dados_dea = os.path.join(DIRETORIO_DADOS_INTERMEDIARIOS, 'amostra.xlsx')
    df = pd.read_excel(arquivo_dados_dea)

    # Executa DEA
    modelo_tcu.executa_por_cluster(arquivo_dados_dea, DIRETORIO_DADOS_RESULTADOS, 'CLUSTER')
