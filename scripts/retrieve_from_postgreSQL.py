import os

import psycopg2
from sqlalchemy import create_engine
import pandas as pd
import numpy as np



# Função que retorna 'SIM' se a observação "row_value" da coluna "column_name" pertence ao conjunto de...
# valores da coluna "column_name" do objeto "dataframe"; caso contrário a função retorna 'NÃO'
def binary_labeled_column(dataframe, column_name, row_value):
    if row_value[column_name] in set(dataframe[column_name]):
        return 'SIM'
    else:
        return 'NÃO'


def retrieve(db_name, db_user, db_password, first_year, last_year):


    # Dados de conexão
    DB_NAME = db_name
    DB_USER = db_user
    DB_PASS = db_password
    DB_TYPE = 'postgresql'
    DB_HOST = '127.0.0.1'
    DB_PORT = '5432'
    DB_DRIVER = 'psycopg2'

    # URI
    DATABASE_URI = '%s+%s://%s:%s@%s:%s/%s' % (DB_TYPE, DB_DRIVER, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)
    # Criação do engine de conexão com o banco de dados DB_NAME
    engine = create_engine(DATABASE_URI)

    # Itera sobre os anos
    for year in np.arange(first_year, last_year + 1):
        print(year)
        # Criação do arquivo xlsx de dados dos meses do ano "year"
        with pd.ExcelWriter('Tabela_DEA_Meses_de_' + str(year) + '.xlsx') as writer:
            # Itera sobre os meses do ano "year"
            for month in np.arange(1, 13):
                month = str(month)
                month = month.zfill(2)
                print(month)
                # Queries no CNES local:

                # Construção da coluna CNES_SALAS_AMBULATORIAIS no mês "month" do ano "year"
                df1 = pd.read_sql(f'''SELECT "CNES_ID",
                                             "UF_ST" AS "UF",
                                             "MUNNOME",
                                             "GESTAO",
                                             "ATIVIDADE",
                                             "TIPO",
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
                df2 = pd.read_sql(f'''SELECT "CNES_ID",
                                             CAST(SUM("QT_SUS") AS INTEGER) AS "CNES_LEITOS_SUS"
                                      FROM cnes_lt.ltbr
                                      WHERE "ANO_LT" = {year} AND "MES_LT" = '{month}'
                                      GROUP BY "CNES_ID"
                                      ORDER BY "CNES_ID"
                                   ''', con=engine)

                # Merge de df1 e df2 por df1 pela coluna CNES_ID
                df1 = pd.merge(df1, df2, how='left', left_on='CNES_ID', right_on='CNES_ID')
                # Substituição de NaN por 0
                df1.fillna(0, inplace=True)
                # Colocação dos valores da coluna como tipo int
                df1['CNES_LEITOS_SUS'] = df1['CNES_LEITOS_SUS'].astype(int)

                # Construção da coluna CNES_MEDICOS no mês "month" do ano "year"
                df3 = pd.read_sql(f'''SELECT "CNES_ID",
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

                # Merge de df1 e df3 por df1 pela coluna CNES_ID
                df1 = pd.merge(df1, df3, how='left', left_on='CNES_ID', right_on='CNES_ID')
                # Substituição de NaN por 0
                df1.fillna(0, inplace=True)
                # Colocação dos valores da coluna como tipo int
                df1['CNES_MEDICOS'] = df1['CNES_MEDICOS'].astype(int)

                # Construção da coluna CNES_PROFISSIONAIS_ENFERMAGEM no mês "month" do ano "year"
                df4 = pd.read_sql(f'''SELECT "CNES_ID",
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

                # Merge de df1 e df4 por df1 pela coluna CNES_ID
                df1 = pd.merge(df1, df4, how='left', left_on='CNES_ID', right_on='CNES_ID')
                # Substituição de NaN por 0
                df1.fillna(0, inplace=True)
                # Colocação dos valores da coluna como tipo int
                df1['CNES_PROFISSIONAIS_ENFERMAGEM'] = df1['CNES_PROFISSIONAIS_ENFERMAGEM'].astype(int)

                # Construção da coluna FILANTROPICO no mês "month" do ano "year"
                df5 = pd.read_sql(f'''SELECT DISTINCT "CNES_ID"
                                      FROM cnes_ef.efbr
                                      WHERE "ANO_EF" = {year} AND "MES_EF" = '{month}'
                                   ''', con=engine)

                # Uso da função "binary_labeled_column" definida neste módulo para criação da coluna "FILANTROPICO"...
                # em df1 com base em df5
                df1['FILANTROPICO'] = df1.apply(lambda x: binary_labeled_column(df5, 'CNES_ID', x), axis=1)

                # Reordena as colunas de df1
                df1 = df1[['CNES_ID', 'UF', 'MUNNOME', 'GESTAO', 'ATIVIDADE', 'TIPO',
                           'NAT_JURIDICA', 'FILANTROPICO', 'CNES_SALAS', 'CNES_LEITOS_SUS',
                           'CNES_MEDICOS', 'CNES_PROFISSIONAIS_ENFERMAGEM']]

                # Queries SIH local:
                # Construção das colunas SIH_QTD e SIH_VALOR no mês "month" do ano "year"
                df6 = pd.read_sql(f'''SELECT "CNES_ID",
                                             COUNT("N_AIH") AS "SIH_QTD",
                                             ROUND(SUM("VAL_TOT")::NUMERIC, 2) as "SIH_VALOR"
                                      FROM sih_rd.rdbr
                                      WHERE "ANO_RD" = {year} AND "MES_RD" = '{month}'
                                      GROUP BY "CNES_ID"
                                   ''', con=engine)

                # Merge de df1 e df6 por df1 pela coluna CNES_ID
                df1 = pd.merge(df1, df6, how='left', left_on='CNES_ID', right_on='CNES_ID')
                # Substituição de NaN por 0
                df1.fillna(0, inplace=True)
                # Colocação dos valores da coluna como tipo int
                df1['SIH_QTD'] = df1['SIH_QTD'].astype(int)

                # Queries SIA local:
                # Construção das colunas SIA_QTD e SIA_VALOR no mês "month" do ano "year"
                df7 = pd.read_sql(f'''SELECT "PACODUNI_ID" AS "CNES_ID",
                                             CAST(SUM("PA_QTDAPR") AS INTEGER) AS "SIA_QTD",
                                             ROUND(SUM("PA_VALAPR")::NUMERIC, 2) AS "SIA_VALOR"
                                      FROM sia_pa.pabr
                                      WHERE "ANO_PA" = {year} AND "MES_PA" = '{month}'
                                      GROUP BY "PACODUNI_ID"
                                   ''', con=engine)

                # Merge de df1 e df7 por df1 pela coluna CNES_ID
                df1 = pd.merge(df1, df7, how='left', left_on='CNES_ID', right_on='CNES_ID')
                # Substituição de NaN por 0
                df1.fillna(0, inplace=True)
                # Colocação dos valores da coluna como tipo int
                df1['SIA_QTD'] = df1['SIA_QTD'].astype(int)

                # Transfere df1 para uma planilha denominada "'year'_'month'" num arquivo xlsx denominado "Tabela_DEA_Meses_de_'year'"
                df1.to_excel(writer, sheet_name=f'{str(year)}_{month}', index=False)



if __name__ == '__main__':

    retrieve('dbsus', 'Eric', 'teste', 2017, 2019)
