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

        # Cria string com o conteúdo do arquivo de parâmetros
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

            # Executa modelo
            print('Treinando modelo DEA com dados da planilha "{}"'.format(data_file))
            PyDEAMain.main(filename=arquivo_parametros_tmp.name, output_dir=diretorio_saida)
            print('Treino concluído.\n\n')

    def executa_por_cluster(self, data_file, diretorio_saida, coluna_cluster):
        """
        Executa a análise DEA separadamente em cada subconjunto da planilha de entrada identificados pelos
        valores da coluna_cluster. Ao final, os resultados para cada cluster são salvos no diretorio_saida
        e uma cópia da planilha de entrada é salva com a coluna EFICIENCIA adicionada com os escores calculados
        para cada DMU não normalizados.
        """
        # Obtém lita de clusters
        df = pd.read_excel(data_file)
        clusters = df[coluna_cluster].unique()

        # Obtém diretório temporário
        diretorio_temporario = tempfile.gettempdir()

        # Adiciona coluna para o score DEA ao df
        df['EFICIENCIA'] = -1

        # Para cada cluster
        for cluster in clusters:

            print('Treinando DEA para cluster {cluster}...'.format(cluster=cluster))

            # Obtém df somente com unidades do cluster
            df_filtrado = df[df[coluna_cluster] == cluster]

            # Remove colunas que não possuem entradas e saídas para a DEA
            lista_colunas_sem_coluna_cluster = df_filtrado.columns.to_list()
            lista_colunas_sem_coluna_cluster.remove(coluna_cluster)
            lista_colunas_sem_coluna_cluster.remove('EFICIENCIA')
            df_filtrado = df_filtrado[lista_colunas_sem_coluna_cluster]

            # Arquivo para salvar temporariamente o df com registros do cluster
            arquivo_entrada_basename = os.path.basename(os.path.splitext(data_file)[0])
            arquivo_df_cluster = os.path.join(diretorio_temporario, '{arquivo_entrada}_cluster_{cluster}.xlsx'
                                              .format(arquivo_entrada=arquivo_entrada_basename, cluster=cluster))

            # Salva arquivo
            df_filtrado.to_excel(arquivo_df_cluster)

            # Executa DEA no arquivo de saída
            self.executa(arquivo_df_cluster, diretorio_saida)

            # Carrega resultados do arquivo
            arquivo_resultado_basename = os.path.splitext(os.path.basename(arquivo_df_cluster))[0] + '_result.xlsx'
            arquivo_resultado = os.path.join(diretorio_saida, arquivo_resultado_basename)
            df_resultado = pd.read_excel(arquivo_resultado, skiprows=1)

            # Adicionar resultado de eficiência ao dataframe original e salva resultado
            df.loc[df.index[df[coluna_cluster] == cluster], 'EFICIENCIA'] = df_resultado.Efficiency.to_list()

        # Salva arquivo de entrada com a coluna EFICIENCIA com respectivos escores DEA
        arquivo_entrada_basename = os.path.basename(os.path.splitext(data_file)[0])
        arquivo_resultado_final = os.path.join(
            diretorio_saida, 'resultado_{arquivo_entrada}.xlsx'.format(arquivo_entrada=arquivo_entrada_basename)
        )
        df.to_excel(arquivo_resultado_final, index=False)

        return df
