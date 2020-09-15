import obtem_dados_specific
import obtem_dados_range
from clusteriza import clusteriza
from prepara_dados import prepara_dados_specific, prepara_dados_range
from executa_dea import executa_deas



def main_specific(DATABASE_URI, year=2019):

    first_year = int(first_period[3:])
    last_year = int(last_period[3:])

    obtem_dados_specific(DATABASE_URI, year)
    clusteriza(year)
    prepara_dados_specific(year)
    executa_dea(year)


def main_range(DATABASE_URI, first_period='01-2017', last_period='12-2019'):

    first_year = int(first_period[3:])
    last_year = int(last_period[3:])

    obtem_dados_range(DATABASE_URI, first_period, last_period)
    clusteriza(first_year, last_year)
    prepara_dados_range(first_period, last_period)
    executa_deas(first_period, last_period)



if __name__ == '__main__':

    # Dados de conexão
    DB_NAME = 'dbsus'
    DB_USER = 'Eric'
    DB_PASS = 'teste'
    DB_TYPE = 'postgresql'
    DB_HOST = '127.0.0.1'
    DB_PORT = '5432'
    DB_DRIVER = 'psycopg2'

    tipo = input('Deseja realizar DEA para um ano específico ou faixa de meses (1 ou 2)? \n')

    # URI
    DATABASE_URI = '%s+%s://%s:%s@%s:%s/%s' % (DB_TYPE, DB_DRIVER, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)

    if tipo == '1':

        main_specific(DATABASE_URI, 2019)

    else:

        main_range(DATABASE_URI, '01-2017', '02-2020')
