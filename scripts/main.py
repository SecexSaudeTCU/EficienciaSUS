from obtem_dados import obtem_dados
from clusteriza import clusteriza
from prepara_dados_range import prepara_dados_range
from executa_dea import executa_deas



def main(db_name, db_user, db_password, first_period='01-2017', last_period='12-2019'):

    first_year = int(first_period[3:])
    last_year = int(last_period[3:])

    obtem_dados(db_name, db_user, db_password, first_year,last_year)
    clusteriza(first_year,last_year)
    prepara_dados_range(first_period, last_period)
    executa_deas(first_period, last_period)


main('dbsus', 'Eric', 'teste', '01-2017', '12-2019')
