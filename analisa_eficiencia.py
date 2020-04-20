"""
Script para analisar escores de eficiência obtidos pela análise DEA.
"""

import os
import pandas as pd

if __name__ == '__main__':

    # Obtem diretório raiz do projeto
    DIRETORIO_RAIZ_PROJETO = os.path.dirname(os.path.realpath(__file__))

    # Diretórios de dados e resultados
    DIRETORIO_DADOS_INTERMEDIARIOS = os.path.join(DIRETORIO_RAIZ_PROJETO, 'dados', 'intermediarios')
    DIRETORIO_DADOS_RESULTADOS = os.path.join(DIRETORIO_RAIZ_PROJETO, 'dados', 'resultados')

    # Carrega resultados da análise DEA por cluster
    arquivo_resultado_2018 = os.path.join(DIRETORIO_RAIZ_PROJETO, 'dados', 'resultados', 'resultado_hosp_pubs_2018_clusterizado.xlsx')
    df_resultado = pd.read_excel(arquivo_resultado_2018)

    # Remove undiades com eficiência 'Infeasible' ou 'Unbounded'
    df_feasible = df_resultado[pd.to_numeric(df_resultado.EFICIENCIA, errors='coerce').notnull()]
    df_feasible.EFICIENCIA = df_feasible.EFICIENCIA.astype('float')

    # Substuir NANs na coluna indicando a gestão por OSS
    df_feasible.SE_GERIDA_OSS = df_feasible.SE_GERIDA_OSS.fillna('NA')

    # Calcula médias e desvios padrões por cluster
    medias = df_feasible.groupby(['CLUSTER']).EFICIENCIA.mean().to_dict()
    desvios = df_feasible.groupby(['CLUSTER']).EFICIENCIA.std().to_dict()

    # Padroniza escores por cluster
    std_scores = pd.Series([
        (e - medias[c]) / desvios[c] for c, e in zip(df_feasible.CLUSTER.to_list(), df_feasible.EFICIENCIA.to_list())
    ])

    # Normaliza eficiências para o intervalor de 0 a 1
    df_feasible.loc[:, 'EFICIENCIA_NORMALIZADA'] = ((std_scores - std_scores.min()) / (std_scores.max() - std_scores.min())).values


    df_feasible.EFICIENCIA_NORMALIZADA.hist(bins=300)

    df_feasible.groupby('SE_GERIDA_OSS').EFICIENCIA_NORMALIZADA.mean()

    """
    Avaliar a ordenação das médias das eficiências dos TIPO_UNIDADEs e verificar que elas são explicadas pelas seguintes regras:
      ESPECIALIZADO > GERAL, 
      PRONTO-SOCORRO > HOSPITAL, 
      MISTA = GERAL + SOCORRO, 
      H.DIA/ISOLADO é exceção.
    """
    df_feasible.groupby('TIPO_UNIDADE').EFICIENCIA_NORMALIZADA.mean().sort_values()

    """
    Avaliar a ordenação das médias das eficiências da ATIVIDADE_ENSINO e verificar que elas são explicadas pelas seguintes regras:
      MAIS ENSINO == MAIS EFICIENTE
    """
    df_feasible.groupby('ATIVIDADE_ENSINO').EFICIENCIA_NORMALIZADA.mean().sort_values()

    """
    Nenhum padrão óbvio identificado.
    """
    df_feasible.groupby('NAT_JURIDICA').EFICIENCIA_NORMALIZADA.mean().sort_values()



    df_feasible.groupby('ESFERA_FEDERATIVA').EFICIENCIA_NORMALIZADA.mean().sort_values()
    df_feasible.groupby('FAIXA_LEITOS').EFICIENCIA_NORMALIZADA.mean().sort_values()
    df_feasible.groupby('TIPO_ADMIN_PUB').EFICIENCIA_NORMALIZADA.mean().sort_values()
    df_feasible.groupby('REGIAO').EFICIENCIA_NORMALIZADA.mean().sort_values()
    df_feasible.groupby('UF').EFICIENCIA_NORMALIZADA.mean().sort_values()
