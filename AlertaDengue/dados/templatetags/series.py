from datetime import timedelta
from django import template
from time import mktime

from dados.dbdata import load_series, get_series_by_UF

import json

register = template.Library()


def int_or_none(x):
    return None if x is None else int(x)


@register.inclusion_tag("series_plot.html", takes_context=True)
def alerta_series(context):
    disease = (
        'dengue' if 'disease_code' not in context else
        context['disease_code']
    )

    dados = load_series(
        context['geocodigo'], disease
    )[context['geocodigo']]

    if dados is None:
        return {
            'nome': context['nome'],
            'dados': {},
            'start': {},
            'verde': {},
            'amarelo': {},
            'laranja': {},
            'vermelho': {},
        }

    dados['dia'] = [
        int(mktime((d + timedelta(7)).timetuple()))
        for d in dados['dia']]

    # green alert
    ga = [
        int(c) if a == 0 else None
        for a, c in zip(dados['alerta'], dados['casos'])]
    ga = [
        int_or_none(dados['casos'][n])
        if i is None and ga[n - 1] is not None else int_or_none(i)
        for n, i in enumerate(ga)]
    # yellow alert
    ya = [
        int(c) if a == 1 else None
        for a, c in zip(dados['alerta'], dados['casos'])]
    ya = [
        int_or_none(dados['casos'][n])
        if i is None and ya[n - 1] is not None else int_or_none(i)
        for n, i in enumerate(ya)]
    # orange alert
    oa = [
        int(c) if a == 2 else None
        for a, c in zip(dados['alerta'], dados['casos'])]
    oa = [
        int_or_none(dados['casos'][n])
        if i is None and oa[n - 1] is not None else int_or_none(i)
        for n, i in enumerate(oa)]
    # red alert
    ra = [
        int(c) if a == 3 else None
        for a, c in zip(dados['alerta'], dados['casos'])]
    ra = [
        int_or_none(dados['casos'][n])
        if i is None and ra[n - 1] is not None else int_or_none(i)
        for n, i in enumerate(ra)]

    return {
        'nome': context['nome'],
        'dados': dados,
        'start': dados['dia'][0],
        'verde': json.dumps(ga),
        'amarelo': json.dumps(ya),
        'laranja': json.dumps(oa),
        'vermelho': json.dumps(ra),
    }


@register.inclusion_tag("total_series.html", takes_context=True)
def total_series(context):
    # gc = context['geocodigos'][0]
    series = get_series_by_UF()
    ufs = list(set(series.uf.tolist()))
    # 51 weeks to get the end of the SE
    start = series.data.max() - timedelta(weeks=51)
    start = int(mktime(start.timetuple()))
    casos = {}
    casos_est = {}

    for uf in ufs:
        series_uf = series[series.uf == uf]
        datas = [
            int(mktime(d.timetuple())) * 1000
            for d in series_uf.data[-52:]
        ]
        casos[uf] = [
            list(t)
            for t in zip(
                datas,
                series_uf.casos_s[-52:].astype('int').tolist()
            )
        ]
        casos_est[uf] = [
            list(t)
            for t in zip(
                datas,
                series_uf.casos_est_s[-52:].astype('int').tolist()
            )
        ]

    return {
        'ufs': ufs,
        'start': start,
        'series': casos,
        'series_est': casos_est
    }
