"""
Wrapper para a biblioteca PyDEA para permitir seu uso no código Python.

Nota: este wrapper foi feito com as funcionalidades mínimas para uso neste trabalho.
"""

import os
import tempfile

import pandas as pd
from pyDEA import main as PyDEAMain

import consts



TEMPLATE_ARQUIVO_PARAMETROS = """
    <PRICE_RATIO_RESTRICTIONS> {{}}
    <DATA_FILE> {{{data_file}}}
    <OUTPUT_CATEGORIES> {{{output_categories}}}
    <INPUT_CATEGORIES> {{{input_categories}}}
    <VIRTUAL_WEIGHT_RESTRICTIONS> {{{virtual_weight_restrictions}}}
    <PEEL_THE_ONION> {{}}
    <MULTIPLIER_MODEL_TOLERANCE> {{0}}
    <RETURN_TO_SCALE> {{VRS}}
    <OUTPUT_FILE> {{}}
    <DEA_FORM> {{multi}}
    <ORIENTATION> {{output}}
    <ABS_WEIGHT_RESTRICTIONS> {{}}
    <CATEGORICAL_CATEGORY> {{}}
    <MAXIMIZE_SLACKS> {{}}
    <NON_DISCRETIONARY_CATEGORIES> {{}}
    <USE_SUPER_EFFICIENCY> {{yes}}
    <WEAKLY_DISPOSAL_CATEGORIES> {{}}
"""

class ModeloDEA:
    """
    Modelo para encapsualar o instanciamento e execução da análise utilizando o PyDEA
    """

    def __init__(self, input_categories, output_categories, virtual_weight_restrictions):
        """
        Instancia o modelo DEA do PyDEA com os parâmetros relevantes para nossos experimentos.
        """
        self.input_categories = input_categories
        self.output_categories = output_categories
        self.virtual_weight_restrictions = virtual_weight_restrictions

    def executa(self, data_file, diretorio_saida):
        """
        Executa a análise DEA e salva resultados no diretorio_saida.

        Nota: a primeira coluna deve conter os nomes das DMUs.
        """

        # Lê o arquivo "data_file" (imbuído do PATH) como um objeto pandas DataFrame
        df = pd.read_excel(data_file)
        # Mantém em "df" somente 1ª coluna (nomes das DMUs) e colunas utilizadas na DEA (entradas e saídas)
        df = df[[df.columns[0]] + self.input_categories + self.output_categories]

        # Coleta apenas o nome do arquivo de "data_file"
        arquivo_entrada_basename = os.path.basename(data_file)

        # Cria diretório temporário para o arquivo de nome "arquivo_entrada_basename"
        arquivo_entrada_temp = os.path.join(tempfile.gettempdir(), arquivo_entrada_basename)
        # Coloca os dados de "df" num arquivo "xlsx" localizado no diretório temporário
        df.to_excel(arquivo_entrada_temp, index=False)

        # Cria string com o conteúdo do arquivo de parâmetros "TEMPLATE_ARQUIVO_PARAMETROS"
        params_file = TEMPLATE_ARQUIVO_PARAMETROS.format(
            data_file=arquivo_entrada_temp,
            input_categories=';'.join(self.input_categories),
            output_categories=';'.join(self.output_categories),
            virtual_weight_restrictions=';'.join(self.virtual_weight_restrictions)
        )

        # Cria arquivo temporário com os parâmetros do modelo
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, prefix='pydea_') as arquivo_parametros_tmp:

            # Escreve parâmetros no arquivo
            arquivo_parametros_tmp.write(params_file)

            # Retorna o ponteiro para o início do arquivo
            arquivo_parametros_tmp.seek(0)

            print('Treinando modelo DEA com dados da planilha "{}"'.format(data_file))
            # Executa modelo
            PyDEAMain.main(filename=arquivo_parametros_tmp.name, output_dir=diretorio_saida)
            print('Treino concluído.\n\n')

    def executa_por_cluster(self, data_file, diretorio_saida, coluna_cluster):
        """
        Executa a análise DEA separadamente em cada subconjunto da planilha de entrada identificados pelos
        valores da coluna_cluster. Ao final, os resultados para cada cluster são salvos no diretorio_saida
        e uma cópia da planilha de entrada é salva com a coluna EFICIENCIA adicionada com os escores calculados
        para cada DMU não normalizados.
        """
        # Lê o arquivo "data_file" (imbuído do PATH) como um objeto pandas DataFrame
        df = pd.read_excel(data_file)

        # Obtém objeto Numpy ndarray dos valores únicos de numeração de cluster contidos...
        # na coluna coluna_cluster de "df"
        clusters = df[coluna_cluster].unique()

        # Cria diretório temporário
        diretorio_temporario = tempfile.gettempdir()

        # Adiciona coluna para o score DEA ao df
        df['EFICIENCIA'] = -1

        # Itera sobre cada numeração de cluster
        for cluster in clusters:

            print('Treinando DEA para cluster {cluster}...'.format(cluster=cluster))

            # Obtém objeto pandas DataFrame somente com unidades hospitalares do cluster "cluster"
            df_filtrado = df[df[coluna_cluster] == cluster]

            # Obtém objeto list dos nomes das colunas de "df_filtrado"
            lista_colunas_sem_coluna_cluster = df_filtrado.columns.to_list()
            # Remove o objeto string coluna_cluster do referido objeto list
            lista_colunas_sem_coluna_cluster.remove(coluna_cluster)
            # Remove o objeto string "EFICIENCIA" do referido objeto list
            lista_colunas_sem_coluna_cluster.remove('EFICIENCIA')
            # Reconstroi "df_filtrado" apenas com as colunas presentes em "lista_colunas_sem_coluna_cluster"
            df_filtrado = df_filtrado[lista_colunas_sem_coluna_cluster]

            # Coleta o nome do arquivo "data_file" sem extensão
            arquivo_entrada_basename = os.path.basename(os.path.splitext(data_file)[0])
            # Cria arquivo "xlsx" do cluster "cluster" no diretório temporário
            arquivo_df_cluster = os.path.join(diretorio_temporario, '{arquivo_entrada}_cluster_{cluster}.xlsx'
                                              .format(arquivo_entrada=arquivo_entrada_basename, cluster=cluster))

            # Coloca os dados de "df_filtrado" no arquivo "xlsx" do cluster "cluster" localizado...
            # no diretório temporário
            df_filtrado.to_excel(arquivo_df_cluster)

            # Chama o método "executa" da mesma class
            self.executa(arquivo_df_cluster, diretorio_saida)

            # Coleta o nome do arquivo "arquivo_df_cluster" sem extensão e acresce o objeto string "_result.xlsx"
            arquivo_resultado_basename = os.path.splitext(os.path.basename(arquivo_df_cluster))[0] + '_result.xlsx'
            # Cria arquivo "xlsx" de resultados do cluster "cluster" no diretório "diretorio_saida"
            arquivo_resultado = os.path.join(diretorio_saida, arquivo_resultado_basename)
            print(arquivo_resultado)
            # Lê o arquivo em formato "xlsx" "arquivo_resultado" como um objeto pandas DataFrame...
            # e desconsidera a primeira linha
            df_resultado = pd.read_excel(arquivo_resultado, skiprows=1)

            # Adiciona resultado de eficiência ao dataframe original e salva resultado
            df.loc[df.index[df[coluna_cluster] == cluster], 'EFICIENCIA'] = df_resultado['Efficiency'].to_list()

        # Remove undiades com eficiência 'Infeasible' ou 'Unbounded'
        df_feasible = df[pd.to_numeric(df['EFICIENCIA'], errors='coerce').notnull()]
        df_feasible['EFICIENCIA'] = df_feasible['EFICIENCIA'].astype('float')

        # Calcula médias e desvios padrões por cluster
        medias = df_feasible.groupby(['CLUSTER'])['EFICIENCIA'].mean().to_dict()
        desvios = df_feasible.groupby(['CLUSTER'])['EFICIENCIA'].std().to_dict()

        # Padroniza escores por cluster
        std_scores = pd.Series([
            (e - medias[c]) / desvios[c] for c, e in zip(df_feasible['CLUSTER'].to_list(), df_feasible['EFICIENCIA'].to_list())
        ])

        # Normaliza eficiências para o intervalo de 0 a 1
        df_feasible.loc[:, 'EFICIENCIA_NORMALIZADA'] = ((std_scores - std_scores.min()) / (std_scores.max() - std_scores.min())).values

        # Salva arquivo de entrada com as colunas EFICIENCIA e EFICIENCIA_NORMALIZADA com respectivos escores DEA
        arquivo_entrada_basename = os.path.basename(os.path.splitext(data_file)[0])
        arquivo_resultado_final = os.path.join(
            diretorio_saida, 'resultado_{arquivo_entrada}.xlsx'.format(arquivo_entrada=arquivo_entrada_basename)
        )
        df_feasible.to_excel(arquivo_resultado_final, index=False)

        return df
