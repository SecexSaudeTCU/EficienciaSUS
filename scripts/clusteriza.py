"""
Clusteriza com k-means as unidades hospitalares e salva planilhas com a coluna CLUSTER adicionada com os respectivos
clusters encontrados.

Nota:
O número k de clusters é determinado automaticamente. Para a análise DEA, segundo [Cooper et al, 2011], o número mínimo
de DMUs deve ser superior a três vezes a soma de variáveis de entrada e saída. Portanto, o número de cluster k é
determinado como o maior possível que não gere clusters com menos de 15 DMUs (3 vezes número de variáveis de entrada e
saídas que estamos utilizando na DEA).

Após a clusterização, são feitas algumas análises, explicadas com mais detalhes abaixo.
TODO: mover estas análises para script próprio
"""

import os

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

import consts

def distancia_x_reta_ab(x, a, b):
    """
    Calcula a distância do ponto x à reta formada pelos pontos a e b
    """

    return np.linalg.norm(np.cross(b - a, a - x))/np.linalg.norm(b - a)



if __name__ == '__main__':

    # Número mínimo de unidades por cluster (3 x o número de inputs e outputs utilizadas na DEA)
    NUMERO_MINIMO_UNIDADES_POR_CLUSTER = 3 * (4 + 1)

    # Coleta PATH do arquivo "xlsx" gerado no script prepara_dados.py
    arquivo_para_clusterizacao = os.path.join(consts.DIRETORIO_DADOS, 'hosp_pubs_{ANO}.xlsx'.format(ANO=consts.ANO))
    # Lê o arquivo "xlsx" referido como um objeto pandas DataFrame e coloca a coluna CNES como índice
    df_hosp_pubs = pd.read_excel(arquivo_para_clusterizacao, index_col='CNES')

    # Coleta o index do elemento 'SIA-0101' pertencente ao objeto list "df_hosp_pubs.columns.to_list()"
    index_coluna_primeiro_proc = df_hosp_pubs.columns.to_list().index('SIA-0101')
    # Coleta os nomes das colunas de procedimentos de "df_hosp_pubs" como um objeto list
    colunas_para_clust = df_hosp_pubs.columns[index_coluna_primeiro_proc:].to_list()
    # Cria objeto pandas DataFrame apenas das colunas de procedimentos
    df_para_clust = df_hosp_pubs[colunas_para_clust]

    # Inicializa objeto list
    WCSS = [] # WCSS = Within-Cluster Sum of Squares

    # Objeto list cujos elementos correspondem à quantidade de clusters
    K = list(range(1, 30))

    # Itera sobre as quantidades de clusters
    for k in K:
        # Inicialização de instância da class KMeans
        kmeans = KMeans(n_clusters=k)
        # Treinamento do modelo KMeans
        kmeans.fit(df_para_clust)
        # Aloca o valor da inércia do modelo treinado ao objeto list WCSS
        WCSS.append(kmeans.inertia_)
        # Coleta o número de elementos de cada cluster do modelo treinado por ordem decrescente...
        # de elementos
        num_por_cluster = pd.value_counts(kmeans.labels_).sort_values(ascending=False).to_list()

        # Caso o cluster com menor número de elementos tenha menos do que o NUMERO_MINIMO_UNIDADES_POR_CLUSTER
        if num_por_cluster[-1] < NUMERO_MINIMO_UNIDADES_POR_CLUSTER:
            # Salva o número de clusters da iteração anterior e interrompe o loop
            numero_clusters = k - 1
            break

    # Novo objeto list cujos elementos correspondem à quantidade de clusters que respeitam o...
    # limitante superior NUMERO_MINIMO_UNIDADES_POR_CLUSTER
    K = list(range(1, numero_clusters + 1))
    # Desconsidera do objeto list WCSS apenas o último elemento que foi alocado "indevidamente"
    WCSS = WCSS[:-1]

    # Inicializa objeto list
    D = []
    # Ponto inicial do plano (K, WCCS)
    p1 = np.array([K[0], WCSS[K[0] - 1]])
    # Ponto final do plano (K, WCCS)
    p2 = np.array([K[-1], WCSS[K[-1] - 1]])

    # Itera sobre as quantidades de clusters
    for k in K:
        # Calcula a distância do ponto referente ao cluster k à reta formada pelos pontos...
        # p1 e p2
        d = distancia_x_reta_ab(np.array([k, WCSS[k-1]]), p1, p2)
        # Aloca o valor da distância d ao objeto list D
        D.append(d)

    print('O número ótimo de clusters é:', D.index(max(D)) + 1)

    # Mostra os resultados
    plt.figure(figsize=(10,5))
    plt.plot(K, WCSS, '-bo', label='WCSS')
    plt.plot(K, D, '-ro', label='Distância')
    plt.annotate('Valor ótimo de k', np.array([D.index(max(D)) + 1 + 0.2, WCSS[D.index(max(D))] + 0.2]))
    plt.xlabel('k')
    plt.ylabel('WCSS / Distância')
    plt.title('The Elbow Method showing the optimal k')
    plt.legend()
    plt.show()

    # Número de clusters arbitrado
    NUMERO_CLUSTERS = 10

    # Treina kmeans com o número de cluster identificado anteriormente
    modelo = KMeans(n_clusters=NUMERO_CLUSTERS, random_state=42)
    modelo.fit(df_para_clust)

    # Adiciona a coluna CLUSTER ao dataframe
    df_hosp_pubs.insert(loc=1, column='CLUSTER', value=modelo.labels_)

    # Salva planilha original com a coluna CLUSTER adicionada
    arquivo_dados_basename = os.path.basename(os.path.splitext(arquivo_para_clusterizacao)[0])
    arquivo_dados_clusterizados = os.path.join(consts.DIRETORIO_DADOS, arquivo_dados_basename + '_clusterizado.xlsx')
    df_hosp_pubs.to_excel(arquivo_dados_clusterizados, index=False)
