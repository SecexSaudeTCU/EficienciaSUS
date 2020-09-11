import os

import numpy as np
import pandas as pd

import consts

first_period='01-2017'
last_period='12-2019'

# Coleta a substring referente ao ano e a transforma no tipo int
first_year = int(first_period[3:])

# Coleta a substring referente ao ano e a transforma no tipo int
last_year = int(last_period[3:])

# Coleta a substring do mês
first_month = first_period[:2]

# Coleta a substring do mês
last_month = last_period[:2]

df = pd.read_excel(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'), sheet_name=f'{first_year}-{first_month}')
df['EFICIENCIA'].replace('Unbounded', np.nan, inplace=True)
df['EFICIENCIA'] = df['EFICIENCIA'].astype(float)
df.rename(columns={'EFICIENCIA': f'{first_year}-{first_month}'}, inplace=True)
df = df[['CNES', f'{first_year}-{first_month}']]

# Itera sobre os anos
for ano in np.arange(first_year, last_year + 1):

    print(ano)

    if ano == first_year:

        # Itera sobre os meses do primeiro=último ano de dados
        for mes in np.arange(2, 13):

            # Converte o tipo int referenciado à variável "mes" como tipo string
            mes = str(mes)

            # Preenche com zeros à esquerda a string "mes" até ficar com dois dígitos
            mes = mes.zfill(2)

            print(mes)

            # Lê o arquivo xlsx "resultado_dados_tratados_dea_'ano'_'mes'" como um objeto pandas DataFrame
            df_mes = pd.read_excel(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'), sheet_name=f'{ano}-{mes}')

            #
            df_mes['EFICIENCIA'].replace('Unbounded', np.nan, inplace=True)

            #
            df_mes['EFICIENCIA'] = df_mes['EFICIENCIA'].astype(float)

            #
            df_mes.rename(columns={'EFICIENCIA': f'{first_year}-{mes}'}, inplace=True)

            #
            df = pd.merge(df, df_mes[['CNES', f'{first_year}-{mes}']], how='outer', left_on='CNES', right_on='CNES')

    elif first_year < ano < last_year:

        # Itera sobre os meses do último ano de dados
        for mes in np.arange(1, 13):

            # Converte o tipo int referenciado à variável "mes" como tipo string
            mes = str(mes)

            # Preenche com zeros à esquerda a string "mes" até ficar com dois dígitos
            mes = mes.zfill(2)

            print(mes)

            # Lê o arquivo xlsx "resultado_dados_tratados_dea_'ano'_'mes'" como um objeto pandas DataFrame
            df_mes = pd.read_excel(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'), sheet_name = f'{ano}-{mes}')

            #
            df_mes['EFICIENCIA'].replace('Unbounded', np.nan, inplace=True)

            #
            df_mes['EFICIENCIA'] = df_mes['EFICIENCIA'].astype(float)

            #
            df_mes.rename(columns={'EFICIENCIA': f'{ano}-{mes}'}, inplace=True)

            #
            df = pd.merge(df, df_mes[['CNES', f'{ano}-{mes}']], how='outer', left_on='CNES', right_on='CNES')

    elif ano == last_year:

        # Itera sobre os meses do último ano de dados
        for mes in np.arange(1, int(last_month) + 1):

            # Converte o tipo int referenciado à variável "mes" como tipo string
            mes = str(mes)

            # Preenche com zeros à esquerda a string "mes" até ficar com dois dígitos
            mes = mes.zfill(2)

            print(mes)

            # Lê o arquivo xlsx "resultado_dados_tratados_dea_'ano'_'mes'" como um objeto pandas DataFrame
            df_mes = pd.read_excel(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados.xlsx'), sheet_name = f'{ano}-{mes}')

            #
            df_mes['EFICIENCIA'].replace('Unbounded', np.nan, inplace=True)

            #
            df_mes['EFICIENCIA'] = df_mes['EFICIENCIA'].astype(float)

            #
            df_mes.rename(columns={'EFICIENCIA': f'{ano}-{mes}'}, inplace=True)

            #
            df = pd.merge(df, df_mes[['CNES', f'{ano}-{mes}']], how='outer', left_on='CNES', right_on='CNES')

df.to_excel(os.path.join(consts.DIRETORIO_RESULTADOS, 'resultados_condensados.xlsx'), index=False)
