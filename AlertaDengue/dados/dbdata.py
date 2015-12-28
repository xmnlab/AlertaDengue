"""
Este módulo contem funções para interagir com o banco principal do projeto
 Alertadengue.
"""

import psycopg2
from sqlalchemy import create_engine
from django.conf import settings
import pandas as pd
import numpy as np
from collections import defaultdict
import datetime
from time import mktime


def get_active_cities():
    conexao = create_engine("postgresql://{}:{}@{}/{}".format('dengueadmin', 'aldengue', 'localhost', 'dengue'))
    # sql = 'SELECT DISTINCT municipio_geocodigo, nome from "Municipio"."Historico_alerta" LEFT JOIN "Dengue_global"."Municipio" on municipio_geocodigo = geocodigo'
    sql = 'SELECT DISTINCT municipio_geocodigo from "Municipio"."Historico_alerta"'
    result = conexao.execute(sql)
    municipio_gcs = [add_dv(rec['municipio_geocodigo']) for rec in result]
    municipios = []
    for gc in municipio_gcs:
        res =conexao.execute('SELECT nome from "Dengue_global"."Municipio" where geocodigo={}'.format(gc))
        municipios.append((gc, res.fetchone()['nome']))
    # conexao.close()
    return municipios


def load_series(cidade, doenca='dengue'):
    """
    Monta as séries do alerta para visualização no site
    :param cidade: geocodigo da cidade desejada
    :param doenca: dengue|chik|zika
    :return: dictionary
    """
    conexao = create_engine("postgresql://{}:{}@{}/{}".format('dengueadmin', 'aldengue', 'localhost', 'dengue'))
    ap = str(cidade)
    cidade = int(str(cidade)[:-1])
    dados_alerta = pd.read_sql_query('select * from "Municipio"."Historico_alerta" where municipio_geocodigo={}'.format(cidade), conexao, 'id', parse_dates=True)
    if len(dados_alerta) == 0:
        raise NameError("Não foi possível obter os dados do Banco")

    # tweets = pd.read_sql_query('select * from "Municipio"."Tweet" where "Municipio_geocodigo"={}'.format(cidade), parse_dates=True)
    series = defaultdict(lambda: defaultdict(lambda: []))

    series[ap]['dia'] = dados_alerta.data_iniSE.tolist()
    # series[ap]['tweets'] = [float(i) if not np.isnan(i) else None for i in tweets.numero]
    # series[ap]['tmin'] = [float(i) if not np.isnan(i) else None for i in G.get_group(ap).tmin]
    series[ap]['casos_est_min'] = dados_alerta.casos_est_min.astype(int).tolist()
    series[ap]['casos_est'] = dados_alerta.casos_est.astype(int).tolist()
    series[ap]['casos_est_max'] = dados_alerta.casos_est_max.astype(int).tolist()
    series[ap]['casos'] = dados_alerta.casos.astype(int).tolist()
    series[ap]['alerta'] = (dados_alerta.nivel.astype(int)-1).tolist()  # (1,4)->(0,3)
    series[ap]['SE'] = (dados_alerta.SE.astype(int)).tolist()
    # print(series['dia'])
    series[ap] = dict(series[ap])
    # conexao.close()
    return dict(series)


def get_city_alert(cidade, doenca='dengue'):
    """
    Retorna vários indicadores de alerta a nível da cidade.
    :param cidade: geocódigo
    :param doenca: dengue|chik|zika
    :return: tupla
    """
    series = load_series(cidade, doenca)
    alert = series[str(cidade)]['alerta'][-1]
    SE = series[str(cidade)]['SE'][-1]
    case_series = series[str(cidade)]['casos_est']
    obs_case_series = series[str(cidade)]['casos']
    last_year = series[str(cidade)]['casos'][-52]
    min_max_est = (series[str(cidade)]['casos_est_min'][-1], series[str(cidade)]['casos_est_max'][-1])
    dia = series[str(cidade)]['dia'][-1]
    return alert, SE, case_series, last_year, obs_case_series, min_max_est, dia


def calculate_digit(dig):
    """
    Calcula o digito verificador do geocódigo de município
    :param dig: geocódigo com 6 dígitos
    :return: dígito verificador
    """
    peso = [1, 2, 1, 2, 1, 2, 0]
    soma = 0
    dig = str(dig)
    for i in range(6):
        valor = int(dig[i]) * peso[i]
        soma += sum([int(d) for d in str(valor)]) if valor > 9 else valor
    dv = 0 if soma % 10 == 0 else (10 - (soma % 10))
    return dv


def add_dv(geocodigo):
    """
    Retorna o geocóodigo do município adicionando o digito verificador,, se necessário.
    :param geocodigo: geocóodigo com 6 ou 7 dígitos
    """
    if len(str(geocodigo)) == 7:
        return geocodigo
    else:
        return int(str(geocodigo) + str(calculate_digit(geocodigo)))
