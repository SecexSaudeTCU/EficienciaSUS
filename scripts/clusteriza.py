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
import pandas as pd
from sklearn.cluster import KMeans
from consts import DIRETORIO_DADOS_ORIGINAIS, DIRETORIO_DADOS_INTERMEDIARIOS
import matplotlib.pyplot as plt

if __name__ == '__main__':

    #
    ANO = '2018'

    # Número mínimo de unidades por cluster (3 x o número de variáveis utilizadas na DEA)
    NUMERO_MINIMO_UNIDADES_POR_CLUSTER = 3 * 5

    # Carrega dados da planilha gerada pelo Eric
    arquivo_para_clusterizacao = os.path.join(DIRETORIO_DADOS_INTERMEDIARIOS, 'hosp_pubs_{ANO}.xlsx'.format(ANO=ANO))
    df_hosp_pubs = pd.read_excel(arquivo_para_clusterizacao, index_col='CNES')

    # Cria df somente com as colunas utilizadas na clusterização (as colunas de procedimentos iniciam na SIA-0101)
    idx_coluna_primeiro_proc = df_hosp_pubs.columns.to_list().index('SIA-0101')
    colunas_para_clust = df_hosp_pubs.columns[idx_coluna_primeiro_proc::].to_list()
    df_para_clust = df_hosp_pubs[colunas_para_clust]

    # Número de clusters determinado pela técnica do cotovelo
    NUMERO_CLUSTERS = 10

    # Número mínimo e máximo de cluster para a análise
    MIN_CLUSTERS, MAX_CLUSTERS = 4, 30

    # Inicializa o número de clusters
    numero_clusters = None

    # Treina k-means para cada valor de k
    for k in range(MIN_CLUSTERS, MAX_CLUSTERS):

        # Treina k-means
        modelo = KMeans(n_clusters=k, random_state=42)
        modelo.fit(df_para_clust)

        # Obtém lista de número de elementos por cluster em ordem decrescente
        num_por_cluster = pd.value_counts(modelo.labels_).sort_values(ascending=False).to_list()

        # Caso o cluster com menor número de elementos tenha menos do que o NUMERO_MINIMO_UNIDADES_POR_CLUSTER
        if num_por_cluster[-1] < NUMERO_MINIMO_UNIDADES_POR_CLUSTER:
            # Salva o número de clusters da iteração anterior e interrompe o loop
            numero_clusters = k - 1
            break

    # Treina kmeans com o número de cluster identificado anteriormente
    modelo = KMeans(n_clusters=numero_clusters, random_state=42)
    modelo.fit(df_para_clust)

    # Adiciona a coluna CLUSTER ao dataframe
    df_hosp_pubs.insert(loc=1, column='CLUSTER', value=modelo.labels_)

    # Salva planilha original com a coluna CLUSTER adicionada
    arquivo_dados_basename = os.path.basename(os.path.splitext(arquivo_para_clusterizacao)[0])
    arquivo_dados_clusterizados = os.path.join(DIRETORIO_DADOS_INTERMEDIARIOS,
                                               arquivo_dados_basename + '_clusterizado.xlsx')
    df_hosp_pubs.to_excel(arquivo_dados_clusterizados, index=False)

    """
    TODO: mover o código a seguir para script próprio de análise de resultados
    A Criação dos clusters termina aqui. Após isto, há somente código para análise da clusterização. Ao final da
    execução, o script salva na pasta de resultados intermediários:
        - Gráfico do joelho, mostrando a variação da inércia de acordo com número de clusters
        - Tabela mostrando o número de elementos por cluster de acordo com o valor de k
        - Gráficos de barras mostrando o perfil de procedimentos de cadas cluster
    """

    # Inicializa lista para armazenar as inércias para plotar o gráficodo cotovelo
    inercias = []

    # Inicializa dicionáro para armazenar o número de unidades por cluster (em ordem decrescente)
    num_unidades_por_cluster = {}

    # Treina k-means para cada valor de k
    for k in range(MIN_CLUSTERS, MAX_CLUSTERS):
        # Treina kmeans e salve inércia
        modelo = KMeans(n_clusters=k, random_state=42)
        modelo.fit(df_para_clust)
        inercias.append(modelo.inertia_)

        # Obtém lista de número de elementos por cluster em ordem decrescente
        num_por_cluster = pd.value_counts(modelo.labels_).sort_values(ascending=False).to_list()

        # Adiciona '-'s para tornar que todas as listas de elementos por cluster tenham tamanho k e adiciona ao dict
        num_por_cluster_padded = num_por_cluster + (MAX_CLUSTERS - k - 1) * ['-']
        num_unidades_por_cluster[k] = num_por_cluster_padded

    # Cria dataframe e salva planilha com o número de unidades por cluster
    df_num_por_cluster = pd.DataFrame(num_unidades_por_cluster)
    arquivo_num_por_cluster = os.path.join(DIRETORIO_DADOS_INTERMEDIARIOS,
                                           'num_elementos_por_cluster_{ANO}.xlsx'.format(ANO=ANO))
    df_num_por_cluster.to_excel(arquivo_num_por_cluster)

    # Plota gráfico da variação da inércia de acordo com o número de clusters
    plt.ioff()  # Desabilita o modo iterativo do matplotlib (para não mostrar os gráficos)
    plt.plot(range(MIN_CLUSTERS, MAX_CLUSTERS), inercias, '-o')
    plt.xlabel('Número de clusters')
    plt.ylabel('Inércia')
    plt.title('Gráfico do "cotovelo" para determinação do número de clusters')
    plt.grid()
    plt.xticks(range(MIN_CLUSTERS, MAX_CLUSTERS))
    arquivo_grafico_inercia = os.path.join(DIRETORIO_DADOS_INTERMEDIARIOS, 'kmeans_inercia_vs_k_{ano}.png'.format(ano=ANO))
    plt.savefig(arquivo_grafico_inercia)

    # Carrega mapeamente entre códigos de subgrupos da SIGTAP e suas descrições
    arquivo_mapa_subgrupo_desc = os.path.join(DIRETORIO_DADOS_ORIGINAIS, 'sigtap_mapa_codigo_subgrupo.xlsx')
    df_mapa_subgrupo_desc = pd.read_excel(arquivo_mapa_subgrupo_desc, index_col=0)
    df_mapa_subgrupo_desc.index = ['0' + str(codigo) for codigo in df_mapa_subgrupo_desc.index]
    mapa_subgrupo_desc = dict(zip(df_mapa_subgrupo_desc.index, df_mapa_subgrupo_desc.DESCRICAO))

    # Adiciona a descrição textual ao nome das coluans de procedimentos
    novos_nomes_colunas = {}
    for coluna in df_para_clust.columns:
        codigo = coluna[4:8]
        desc = mapa_subgrupo_desc[codigo]
        novos_nomes_colunas[coluna] = coluna + ' - ' + desc

    # Renomeia colunas
    df_para_clust = df_para_clust.rename(columns=novos_nomes_colunas)

    # Dict para armazenar os centroids
    centroids = {}

    # Para cada cluster
    for k in range(0, NUMERO_CLUSTERS):
        # Obtém hospitais do cluster (Repara que no filtro, utilizamos a variável df_hosp_pubs ao invés da df_cluster)
        df_cluster = df_para_clust[df_hosp_pubs.CLUSTER == k]

        # Obtém centroid
        centroid = df_cluster.mean(axis=0)
        centroids[k] = centroid

        # Plota gráfico de barras para o centroid
        plt.ioff()  # Desabilita o modo iterativo do matplotlib (para não mostrar os gráficos)
        plt.figure(figsize=(10, 25))
        plt.title('Perfil do Cluster {k}'.format(k=k))
        plt.xlabel('Proporção por procedimento (%)')
        plt.ylabel('Procedimento')
        ax = centroid.plot(kind='barh')
        ax.grid()
        ax.set_xlim((0, 1.))
        plt.tight_layout()
        arquivo_grafico_barras_cluster = os.path.join(DIRETORIO_DADOS_INTERMEDIARIOS,
                                                      'cluster_{k}_{ano}.png'.format(ano=ANO, k=k))
        plt.savefig(arquivo_grafico_barras_cluster)

    # Salva planilha com os centroids
    df_centroids = pd.DataFrame(centroids)
    arquivo_centroids = os.path.join(DIRETORIO_DADOS_INTERMEDIARIOS,
                                     'centroids_kmeans_{k}_clusters_{ano}.xlsx'.format(k=NUMERO_CLUSTERS, ano=ANO))
    df_centroids.to_excel(arquivo_centroids)
