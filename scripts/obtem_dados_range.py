import os

import psycopg2
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

import consts



# Função que retorna 'SIM' se a observação "row_value" da coluna "column_name" pertence ao conjunto de...
# valores da coluna "column_name" do objeto "dataframe"; caso contrário a função retorna 'NÃO'
def binary_labeled_column(dataframe, column_name, row_value):
    if row_value[column_name] in set(dataframe[column_name]):
        return 'SIM'
    else:
        return 'NÃO'


def queries_dados_dea(engine, year, month):

        # Queries no CNES local:
        print('Queries no CNES local (PostgreSQL)...')
        # Construção da coluna CNES_SALAS no mês "month" do ano "year"
        df1 = pd.read_sql(f'''SELECT DISTINCT "CNES_ID" AS "CNES",
                                     "UF_ST" AS "UF",
                                     "MUNNOME" AS "MUNICIPIO",
                                     "GESTAO",
                                     "ATIVIDADE" AS "ATIVIDADE_ENSINO",
                                     "TIPO" AS "TIPO_UNIDADE",
                                     "NATUREZA" AS "NAT_JURIDICA",
                                     CAST(COALESCE("QTINST01", 0)
                                          + COALESCE("QTINST02", 0)
                                          + COALESCE("QTINST03", 0)
                                          + COALESCE("QTINST04", 0)
                                          + COALESCE("QTINST05", 0)
                                          + COALESCE("QTINST06", 0)
                                          + COALESCE("QTINST07", 0)
                                          + COALESCE("QTINST08", 0)
                                          + COALESCE("QTINST09", 0)
                                          + COALESCE("QTINST10", 0)
                                          + COALESCE("QTINST11", 0)
                                          + COALESCE("QTINST12", 0)
                                          + COALESCE("QTINST13", 0)
                                          + COALESCE("QTINST14", 0)
                                          + COALESCE("QTINST15", 0)
                                          + COALESCE("QTINST16", 0)
                                          + COALESCE("QTINST17", 0)
                                          + COALESCE("QTINST18", 0)
                                          + COALESCE("QTINST19", 0)
                                          + COALESCE("QTINST20", 0)
                                          + COALESCE("QTINST21", 0)
                                          + COALESCE("QTINST22", 0)
                                          + COALESCE("QTINST23", 0)
                                          + COALESCE("QTINST24", 0)
                                          + COALESCE("QTINST25", 0)
                                          + COALESCE("QTINST26", 0)
                                          + COALESCE("QTINST27", 0)
                                          + COALESCE("QTINST28", 0)
                                          + COALESCE("QTINST29", 0)
                                          + COALESCE("QTINST30", 0)
                                          + COALESCE("QTINST31", 0)
                                          + COALESCE("QTINST32", 0)
                                          + COALESCE("QTINST33", 0)
                                          + COALESCE("QTINST34", 0)
                                          + COALESCE("QTINST35", 0)
                                          + COALESCE("QTINST36", 0)
                                          + COALESCE("QTINST37", 0) AS INTEGER) AS "CNES_SALAS"
                              FROM cnes_st.stbr
                              JOIN cnes_st.codufmun ON cnes_st.stbr."CODUFMUN_ID" = cnes_st.codufmun."ID"
                              JOIN cnes_st.tpgestao ON cnes_st.stbr."TPGESTAO_ID" = cnes_st.tpgestao."ID"
                              JOIN cnes_st.atividad ON cnes_st.stbr."ATIVIDAD_ID" = cnes_st.atividad."ID"
                              JOIN cnes_st.tpunid ON cnes_st.stbr."TPUNID_ID" = cnes_st.tpunid."ID"
                              JOIN cnes_st.natjur ON cnes_st.stbr."NATJUR_ID" = cnes_st.natjur."ID"
                              WHERE "ANO_ST" = {year} AND "MES_ST" = '{month}'
                              ORDER BY "CNES_ID"
                           ''', con=engine)

        # Construção da coluna CNES_LEITOS_SUS no mês "month" do ano "year"
        df2 = pd.read_sql(f'''SELECT "CNES_ID" AS "CNES",
                                     CAST(SUM("QT_SUS") AS INTEGER) AS "CNES_LEITOS_SUS"
                              FROM cnes_lt.ltbr
                              WHERE "ANO_LT" = {year} AND "MES_LT" = '{month}'
                              GROUP BY "CNES_ID"
                              ORDER BY "CNES_ID"
                           ''', con=engine)

        # Merge de df1 e df2 por df1 pela coluna CNES
        df1 = pd.merge(df1, df2, how='left', left_on='CNES', right_on='CNES')
        # Substituição de NaN por 0
        df1.fillna(0, inplace=True)
        # Colocação dos valores da coluna como tipo int
        df1['CNES_LEITOS_SUS'] = df1['CNES_LEITOS_SUS'].astype(int)

        # Construção da coluna CNES_MEDICOS no mês "month" do ano "year"
        df3 = pd.read_sql(f'''SELECT "CNES_ID" AS "CNES",
                                     COUNT(DISTINCT "CNS_PROF") AS "CNES_MEDICOS"
                              FROM cnes_pf.pfbr
                              WHERE "ANO_PF" = {year}
                                    AND "MES_PF" = '{month}'
                                    AND ((SUBSTRING("CBO_ID", 1, 4) = '2231')         /*Médicos*/
                                         OR (SUBSTRING("CBOUNICO_ID", 1, 4) = '2231') /*Médicos*/
                                         OR (SUBSTRING("CBO_ID", 1, 3) = '225')       /*Médicos*/
                                         OR (SUBSTRING("CBOUNICO_ID", 1, 3) = '225')) /*Médicos*/
                              GROUP BY "CNES_ID"
                           ''', con=engine)

        # Merge de df1 e df3 por df1 pela coluna CNES
        df1 = pd.merge(df1, df3, how='left', left_on='CNES', right_on='CNES')
        # Substituição de NaN por 0
        df1.fillna(0, inplace=True)
        # Colocação dos valores da coluna como tipo int
        df1['CNES_MEDICOS'] = df1['CNES_MEDICOS'].astype(int)

        # Construção da coluna CNES_PROFISSIONAIS_ENFERMAGEM no mês "month" do ano "year"
        df4 = pd.read_sql(f'''SELECT "CNES_ID" AS "CNES",
                                     COUNT(DISTINCT "CNS_PROF") AS "CNES_PROFISSIONAIS_ENFERMAGEM"
                              FROM cnes_pf.pfbr
                              WHERE "ANO_PF" = {year}
                                    AND "MES_PF" = '{month}'
                                    AND ((SUBSTRING("CBO_ID", 1, 4) = '2235')            /*Enfermeiros*/
                                         OR (SUBSTRING("CBOUNICO_ID", 1, 4) = '2235')    /*Enfermeiros*/
                                         OR (SUBSTRING("CBO_ID", 1, 4) = '3222')         /*Tecs ou Auxiliares de Enfermagem*/
                                         OR (SUBSTRING("CBOUNICO_ID", 1, 4) = '3222')    /*Tecs ou Auxiliares de Enfermagem*/
                                         OR (SUBSTRING("CBO_ID", 1, 6) = '515110')       /*Atendente de Enfermagem*/
                                         OR (SUBSTRING("CBOUNICO_ID", 1, 6) = '515110')  /*Atendente de Enfermagem*/
                                         OR (SUBSTRING("CBO_ID", 1, 6) = '515135')       /*Socorrista*/
                                         OR (SUBSTRING("CBOUNICO_ID", 1, 6) = '515135')) /*Socorrista*/
                              GROUP BY "CNES_ID"
                           ''', con=engine)

        # Merge de df1 e df4 por df1 pela coluna CNES
        df1 = pd.merge(df1, df4, how='left', left_on='CNES', right_on='CNES')
        # Substituição de NaN por 0
        df1.fillna(0, inplace=True)
        # Colocação dos valores da coluna como tipo int
        df1['CNES_PROFISSIONAIS_ENFERMAGEM'] = df1['CNES_PROFISSIONAIS_ENFERMAGEM'].astype(int)

        # Construção da coluna FILANTROPICO no mês "month" do ano "year"
        df5 = pd.read_sql(f'''SELECT DISTINCT "CNES_ID" AS "CNES"
                              FROM cnes_ef.efbr
                              WHERE "ANO_EF" = {year} AND "MES_EF" = '{month}'
                           ''', con=engine)

        # Uso da função "binary_labeled_column" definida neste módulo para criação da coluna "FILANTROPICO"...
        # em df1 com base em df5
        df1['FILANTROPICO'] = df1.apply(lambda x: binary_labeled_column(df5, 'CNES', x), axis=1)

        # Reordena as colunas de df1
        df1 = df1[['CNES', 'UF', 'MUNICIPIO', 'GESTAO', 'ATIVIDADE_ENSINO', 'TIPO_UNIDADE',
                   'NAT_JURIDICA', 'FILANTROPICO', 'CNES_SALAS', 'CNES_LEITOS_SUS',
                   'CNES_MEDICOS', 'CNES_PROFISSIONAIS_ENFERMAGEM']]

        # Queries SIH local:
        print('Query no SIH local (PostgreSQL)...')
        # Construção da coluna SIH_VALOR no mês "month" do ano "year"
        df6 = pd.read_sql(f'''SELECT "CNES_ID" AS "CNES",
                                     ROUND(SUM("VAL_TOT")::NUMERIC, 2) as "SIH_VALOR"
                              FROM sih_rd.rdbr
                              WHERE "ANO_RD" = {year} AND "MES_RD" = '{month}'
                              GROUP BY "CNES_ID"
                           ''', con=engine)

        # Merge de df1 e df6 por df1 pela coluna CNES
        df1 = pd.merge(df1, df6, how='left', left_on='CNES', right_on='CNES')
        # Substituição de NaN por 0
        df1.fillna(0, inplace=True)

        # Queries SIA local:
        print('Query no SIA local (PostgreSQL)...')
        # Construção da coluna SIA_VALOR no mês "month" do ano "year"
        df7 = pd.read_sql(f'''SELECT "PACODUNI_ID" AS "CNES",
                                     ROUND(SUM("PA_VALAPR")::NUMERIC, 2) AS "SIA_VALOR"
                              FROM sia_pa.pabr
                              WHERE "ANO_PA" = {year} AND "MES_PA" = '{month}'
                              GROUP BY "PACODUNI_ID"
                           ''', con=engine)

        # Merge de df1 e df7 por df1 pela coluna CNES
        df1 = pd.merge(df1, df7, how='left', left_on='CNES', right_on='CNES')
        # Substituição de NaN por 0
        df1.fillna(0, inplace=True)

        # Construção da coluna SIA_SIH_VALOR no mês "month" do ano "year"
        df1['SIA_SIH_VALOR'] = df1['SIA_VALOR'] + df1['SIH_VALOR']
        # Drop as colunas SIA_VALOR e SIH_VALOR
        df1.drop(columns=['SIA_VALOR', 'SIH_VALOR'], inplace=True)

        for coluna in consts.COLUNAS_DEA:
            mascara = df1[coluna] == 0
            df1 = df1[~mascara]
            print(f' * {sum(mascara)} linhas removidas por conter zero na coluna {coluna}')
        print(f'Número de estabelecimentos ao final do processamento: {df1.shape[0]}')

        print('Salvando os dados...')

        # Transfere df1 para o arquivo xlsx denominado "dados_para_dea_'year'_'month'.xlsx"
        df1.to_excel(os.path.join(consts.DIRETORIO_DADOS, f'dados_para_dea_{year}_{month}.xlsx'), index=False)


def obtem_dados_dea(DATABASE_URI, first_period='01-2017', last_period='12-2019'):

    print('Dados para DEA...')

    # Criação do engine de conexão com o banco de dados especificado por "DATABASE_URI"
    engine = create_engine(DATABASE_URI)

    first_year = int(first_period[3:])
    last_year = int(last_period[3:])

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

                print('\n********************************')
                print(f'{year}-{month}')

                queries_dados_dea(engine, ano, mes)

        else:

            # Itera sobre os meses do período
            for mes in np.arange(1, 13):

                # Converte o tipo int referenciado à variável "mes" como tipo string
                mes = str(mes)

                # Preenche com zeros à esquerda a string "mes" até ficar com dois dígitos
                mes = mes.zfill(2)

                print('\n********************************')
                print(f'{ano}-{mes}')

                queries_dados_dea(engine, ano, mes)



def obtem_dados_clusterizacao(DATABASE_URI, first_year=2017, last_year=2019):

    print('Dados para clusterização...')

    # Criação do engine de conexão com o banco de dados especificado por "DATABASE_URI"
    engine = create_engine(DATABASE_URI)

    print('Query no CNES local (PostgreSQL)...')
    #
    df_cnes = pd.read_sql(f'''SELECT DISTINCT "CNES_ID" AS "CNES",
                                     "TIPO" AS "TIPO_UNIDADE",
                                     "NATUREZA" AS "NAT_JURIDICA"
                              FROM cnes_st.stbr
                              JOIN cnes_st.tpunid ON cnes_st.stbr."TPUNID_ID" = cnes_st.tpunid."ID"
                              JOIN cnes_st.natjur ON cnes_st.stbr."NATJUR_ID" = cnes_st.natjur."ID"
                              WHERE "ANO_ST" BETWEEN {first_year} AND {last_year}
                              ORDER BY "CNES_ID"
                           ''', con=engine)

    print('Query no SIH local (PostgreSQL)...')
    #
    df1 = pd.read_sql(f'''SELECT "CNES_ID" AS "CNES",
                                 SUBSTRING("PROCREA_ID", 1, 4) AS "SUBGRP_PROC",
                                 ROUND(SUM("VAL_TOT")::NUMERIC, 2) AS "VALOR_SUBGRP_PROC"
                          FROM sih_rd.rdbr
                          WHERE "ANO_RD" BETWEEN {first_year} AND {last_year}
                          GROUP BY "CNES_ID", "SUBGRP_PROC"
                       ''', con=engine)

    #
    df_sih = df1.copy()

    #
    df_sih['SUBGRP_PROC'] = str('SIH-') + df_sih['SUBGRP_PROC']

    #
    df_sih_per_cnes = df_sih.groupby(['CNES'], as_index=False)['VALOR_SUBGRP_PROC'].sum()

    #
    df_sih_per_cnes.rename(columns={'VALOR_SUBGRP_PROC':'VALOR_SIH'}, inplace=True)

    print('Query no SIA local (PostgreSQL)...')
    #
    df2 = pd.read_sql(f'''SELECT "PACODUNI_ID" AS "CNES",
                                 SUBSTRING("PAPROC_ID", 1, 4) AS "SUBGRP_PROC",
                                 ROUND(SUM("PA_VALAPR")::NUMERIC, 2) AS "VALOR_SUBGRP_PROC"
                          FROM sia_pa.pabr
                          WHERE "ANO_PA" BETWEEN {first_year} AND {last_year}
                          GROUP BY "PACODUNI_ID", SUBSTRING("PAPROC_ID", 1, 4)
                       ''', con=engine)

    #
    df_sia = df2.copy()

    #
    df_sia['SUBGRP_PROC'] = str('SIA-') + df_sia['SUBGRP_PROC']

    #
    df_sia_per_cnes = df_sia.groupby(['CNES'], as_index=False)['VALOR_SUBGRP_PROC'].sum()

    #
    df_sia_per_cnes.rename(columns={'VALOR_SUBGRP_PROC':'VALOR_SIA'}, inplace=True)

    #
    df_sih_sia = pd.concat([df_sih, df_sia])

    #
    total_valor = df_sih_sia.groupby(['CNES'], as_index=False)['VALOR_SUBGRP_PROC'].sum()

    #
    total_valor.rename(columns={'VALOR_SUBGRP_PROC':'VALOR_TOTAL_PER_CNES'}, inplace=True)

    #
    df_sih_sia = pd.merge(df_sih_sia, total_valor, how='left', left_on='CNES', right_on='CNES')

    #
    df_sih_sia.sort_values(['CNES', 'SUBGRP_PROC'])

    #
    df_id_cnes_sih_sia = pd.merge(df_cnes[['CNES']], df_sih_sia, how='left', left_on='CNES', right_on='CNES')

    #
    df_id_cnes_sih_sia['PERCENTUAL_VALOR'] = df_id_cnes_sih_sia['VALOR_SUBGRP_PROC']/df_id_cnes_sih_sia['VALOR_TOTAL_PER_CNES']

    #
    df_id_cnes_sih_sia['PERCENTUAL_VALOR'].fillna(0, inplace=True)

    #
    df_id_cnes_sih_sia = df_id_cnes_sih_sia.drop(['VALOR_SUBGRP_PROC', 'VALOR_TOTAL_PER_CNES'], axis=1)

    #
    df_id_cnes_sih_sia.fillna({'SUBGRP_PROC': 'NONE', 'PERCENTUAL_VALOR': 0.}, inplace=True)

    #
    df_subproc = (df_id_cnes_sih_sia.groupby(['CNES', 'SUBGRP_PROC'])['PERCENTUAL_VALOR'].sum().unstack().fillna(0))

    #
    df_subproc = df_subproc.rename_axis(None, axis=1)

    #
    df_subproc.reset_index(inplace=True)

    #
    df_subproc = df_subproc.drop(['NONE'], axis=1)

    df = pd.merge(df_cnes, df_subproc, how='right', left_on='CNES', right_on='CNES')

    # Coleta o index do elemento 'NAT_JURIDICA' pertencente ao objeto list "df.columns.to_list()"...
    # e acresce o inteiro 1
    pos_col_depois_nat_jur = df.columns.to_list().index('NAT_JURIDICA') + 1
    # Cria objeto list dos valores do objeto dict map_nat_jur chamados pelas chaves k e...
    # contidos no primento elemento do objeto string que constitui a coluna NAT_JURIDICA...
    # de "df_mes"
    nat_jur_simplificada = [consts.MAP_NAT_JUR[k] for k in df['NAT_JURIDICA'].str[0]]
    # Insere em "df" a coluna NAT_JURIDICA_SIMPLIFICADA depois da coluna NAT_JURIDICA tendo...
    # os valores contidos em "nat_jur_simplificada"
    df.insert(loc=pos_col_depois_nat_jur, column='NAT_JURIDICA_SIMPLIFICADA', value=nat_jur_simplificada)

    print('Início:', df.shape)

    # Mantém somente unidades de caráter hospitalar
    df_hosp = df[df['TIPO_UNIDADE'].isin(consts.TIPOS_UNIDADES_MANTIDAS)]

    print('Após remover não-hospitais:', df_hosp.shape)

    # Remove unidades não públicas
    df_hosp_pubs = df_hosp[df_hosp['NAT_JURIDICA_SIMPLIFICADA'] == 'ADMINISTRAÇÂO PÚBLICA']

    print('Após remover entidades não públicas:', df_hosp_pubs.shape)

    print('Salvando os dados...')

    #
    df_hosp_pubs.to_excel(os.path.join(consts.DIRETORIO_DADOS, f'dados_para_clusterizacao_{first_year}_a_{last_year}.xlsx'),
                          index=False)


def obtem_dados(DATABASE_URI, first_period='01-2017', last_period='12-2019'):

    first_year = int(first_period[3:])
    last_year = int(last_period[3:])

    obtem_dados_dea(DATABASE_URI, first_period, last_period)
    obtem_dados_clusterizacao(DATABASE_URI, first_year, last_year)



if __name__ == '__main__':

    # Dados de conexão
    DB_NAME = 'dbsus'
    DB_USER = 'Eric'
    DB_PASS = 'teste'
    DB_TYPE = 'postgresql'
    DB_HOST = '127.0.0.1'
    DB_PORT = '5432'
    DB_DRIVER = 'psycopg2'

    # URI
    DATABASE_URI = '%s+%s://%s:%s@%s:%s/%s' % (DB_TYPE, DB_DRIVER, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)

    obtem_dados(DATABASE_URI, '01-2017', '12-2019')
