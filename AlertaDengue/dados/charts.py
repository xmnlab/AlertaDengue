from datetime import timedelta
from time import mktime

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
from plotly.subplots import make_subplots

# local
from .dbdata import get_series_by_UF


class ReportCityCharts:
    @classmethod
    def create_incidence_chart(
        cls,
        df: pd.DataFrame,
        year_week: int,
        threshold_pre_epidemic: float,
        threshold_pos_epidemic: float,
        threshold_epidemic: float,
    ):
        """
        @see: https://stackoverflow.com/questions/45526734/
            hide-legend-entries-in-a-plotly-figure
        :param df:
        :param year_week:
        :param threshold_pre_epidemic: float,
        :param threshold_pos_epidemic: float
        :param threshold_epidemic: float
        :return:
        """
        df = df.reset_index()[
            ['SE', 'incidência', 'casos notif.', 'level_code']
        ]

        # 200 = 2 years
        df = df[df.SE >= year_week - 200]

        df['SE'] = df.SE.map(lambda v: '%s/%s' % (str(v)[:4], str(v)[-2:]))

        k = 'incidência'

        df['alerta verde'] = df[df.level_code == 1][k]
        df['alerta amarelo'] = df[df.level_code == 2][k]
        df['alerta laranja'] = df[df.level_code == 3][k]
        df['alerta vermelho'] = df[df.level_code == 4][k]

        df['limiar epidêmico'] = threshold_epidemic
        df['limiar pós epidêmico'] = threshold_pos_epidemic
        df['limiar pré epidêmico'] = threshold_pre_epidemic

        figure = make_subplots(specs=[[{"secondary_y": True}]])

        figure.add_trace(
            go.Scatter(
                x=df['SE'],
                y=df['casos notif.'],
                name='Notificações',
                marker={'color': 'rgb(33,33,33)'},
                text=df.SE.map(lambda v: '{}'.format(str(v)[-2:])),
                hoverinfo='text',
                hovertemplate="Semana %{text} : %{y:1f} Casos",
            ),
            secondary_y=True,
        )

        ks_limiar = [
            'limiar pré epidêmico',
            'limiar pós epidêmico',
            'limiar epidêmico',
        ]

        colors = ['rgb(0,255,0)', 'rgb(255,150,0)', 'rgb(255,0,0)']

        for k, c in zip(ks_limiar, colors):
            figure.add_trace(
                go.Scatter(
                    x=df['SE'],
                    y=df[k],
                    name=k.title(),
                    marker={'color': c},
                    text=df.SE.map(lambda v: '{}'.format(str(v)[-2:])),
                    hoverinfo='text',
                    hovertemplate="Semana %{text} : %{y:1f} Casos",
                ),
                secondary_y=True,
            )

        ks_alert = [
            'alerta verde',
            'alerta amarelo',
            'alerta laranja',
            'alerta vermelho',
        ]

        colors = [
            'rgb(0,255,0)',
            'rgb(255,255,0)',
            'rgb(255,150,0)',
            'rgb(255,0,0)',
        ]

        for k, c in zip(ks_alert, colors):
            figure.add_trace(
                go.Bar(
                    x=df['SE'],
                    y=df[k],
                    marker={'color': c},
                    name=k.title(),
                    text=df.SE.map(lambda v: '{}'.format(str(v)[-2:])),
                    hoverinfo='text',
                    hovertemplate="Semana %{text} : %{y:1f} Casos",
                ),
                secondary_y=False,
            )

        figure.update_layout(
            xaxis=dict(
                title='Período (Ano/Semana)',
                tickangle=-60,
                nticks=len(df) // 4,
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
                ticks='outside',
                tickfont=dict(
                    family='Arial', size=12, color='rgb(82, 82, 82)'
                ),
            ),
            yaxis=dict(
                title='Incidência',
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
            ),
            showlegend=True,
            plot_bgcolor='rgb(255, 255, 255)',
            paper_bgcolor='rgb(245, 246, 249)',
            width=1100,
            height=500,
        )

        figure.update_yaxes(
            title_text="Casos",
            secondary_y=True,
            showline=True,
            showgrid=True,
            showticklabels=True,
            linecolor='rgb(204, 204, 204)',
            linewidth=0,
            gridcolor='rgb(204, 204, 204)',
        )

        figure['layout']['legend'].update(
            traceorder='normal',
            font=dict(family='sans-serif', size=12, color='#000'),
            bgcolor='#FFFFFF',
            bordercolor='#E2E2E2',
            borderwidth=1,
        )

        figure['layout'].update(
            title=(
                'Limiares de incidência:: '
                + 'pré epidêmico=%s; '
                + 'pós epidêmico=%s; '
                + 'epidêmico=%s;'
            )
            % (
                '{:.1f}'.format(threshold_pre_epidemic),
                '{:.1f}'.format(threshold_pos_epidemic),
                '{:.1f}'.format(threshold_epidemic),
            ),
            font=dict(family='sans-serif', size=12, color='#000'),
        )

        for trace in figure['data']:
            if trace['name'] == 'casos notif.':
                trace['visible'] = 'legendonly'

        return figure.to_html()

    @classmethod
    def create_climate_chart(
        cls,
        df: pd.DataFrame,
        var_climate,
        year_week,
        climate_crit,
        climate_title,
    ):
        """
        :param df:
        :param var_climate:
        :param year_week:
        :param climate_crit:
        :param climate_title:
        :return:
        """
        k = var_climate.replace('_', '.')

        df_climate = df.reset_index()[['SE', k]]
        df_climate = df_climate[df_climate.SE >= year_week - 200]

        df_climate['SE'] = df_climate.SE.map(
            lambda v: '%s/%s' % (str(v)[:4], str(v)[-2:])
        )

        df_climate['Limiar favorável transmissão'] = climate_crit

        df_climate = df_climate.rename(
            columns={'Limiar favorável transmissão': 'threshold_transmission'}
        )

        df_climate[['SE', 'threshold_transmission', k]].melt('SE')

        figure = go.Figure()

        figure.add_trace(
            go.Scatter(
                x=df_climate['SE'],
                y=df_climate['threshold_transmission'],
                name='Limiar Favorável',
                marker={'color': 'rgb(51, 172, 255)'},
                text=df_climate.SE.map(lambda v: '{}'.format(str(v)[-2:])),
                hoverinfo='text',
                hovertemplate="Semana %{text} : %{y:1f}°C",
            )
        )

        figure.add_trace(
            go.Scatter(
                x=df_climate['SE'],
                y=df_climate[k],
                name='Temperatura min.',
                marker={'color': 'rgb(255,150,0)'},
                text=df_climate.SE.map(lambda v: '{}'.format(str(v)[-2:])),
                hoverinfo='text',
                hovertemplate="Semana %{text} : %{y:1f}°C",
            )
        )

        figure.update_layout(
            # title = "",
            xaxis=dict(
                title='Período (Ano/Semana)',
                tickangle=-60,
                nticks=len(df_climate) // 4,
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
            ),
            yaxis=dict(
                title='Temperatura',
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
                hoverformat=".1f",
            ),
            showlegend=True,
            plot_bgcolor='rgb(255, 255, 255)',
            paper_bgcolor='rgb(245, 246, 249)',
            width=1100,
            height=500,
        )

        figure['layout']['legend'].update(
            x=-0.1,
            y=1.2,
            traceorder='normal',
            font=dict(family='sans-serif', size=12, color='#000'),
            bgcolor='#FFFFFF',
            bordercolor='#E2E2E2',
            borderwidth=1,
        )

        return figure.to_html()

    @classmethod
    def create_tweet_chart(cls, df: pd.DataFrame, year_week):
        """
        :param df:
        :param var_climate:
        :param year_week:
        :param climate_crit:
        :param climate_title:
        :return:
        """
        df_tweet = df.reset_index()[['SE', 'tweets']]
        df_tweet = df_tweet[df_tweet.SE >= year_week - 200]

        df_tweet['SE'] = df_tweet.SE.map(
            lambda v: '%s/%s' % (str(v)[:4], str(v)[-2:])
        )

        df_tweet.rename(columns={'tweets': 'menções'}, inplace=True)

        figure = go.Figure()

        figure.add_trace(
            go.Scatter(
                x=df_tweet['SE'],
                y=df_tweet['menções'],
                name='Menções',
                marker={'color': 'rgb(0,0,255)'},
                text=df_tweet.SE.map(lambda v: '{}'.format(str(v)[-2:])),
                hoverinfo='text',
                hovertemplate="Semana %{text} : %{y} Tweets",
            )
        )

        figure.update_layout(
            # title="",
            xaxis=dict(
                title='Período (Ano/Semana)',
                tickangle=-60,
                nticks=len(df_tweet) // 4,
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
            ),
            yaxis=go.layout.YAxis(
                title='Tweets',
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
            ),
            showlegend=True,
            plot_bgcolor='rgb(255, 255, 255)',
            paper_bgcolor='rgb(245, 246, 249)',
            width=1100,
            height=500,
        )

        figure['layout']['legend'].update(
            x=-0.1,
            y=1.2,
            traceorder='normal',
            font=dict(family='sans-serif', size=12, color='#000'),
            bgcolor='#FFFFFF',
            bordercolor='#E2E2E2',
            borderwidth=1,
        )

        return figure.to_html()


class ReportStateCharts:
    @classmethod
    def create_tweet_chart(cls, df: pd.DataFrame, year_week, disease: str):
        """
        :param df:
        :param year_week:
        :param disease:
        :return:
        """
        ks_cases = ['casos notif. {}'.format(disease)]

        df_tweet = df.reset_index()[['SE', 'tweets'] + ks_cases]
        df_tweet = df_tweet[df_tweet.SE >= year_week - 200]

        df_tweet.rename(columns={'tweets': 'menções'}, inplace=True)

        df_grp = (
            df_tweet.groupby(df.index)[['menções'] + ks_cases]
            .sum()
            .reset_index()
        )

        df_grp['SE'] = df_grp.SE.map(
            lambda v: '%s/%s' % (str(v)[:4], str(v)[-2:])
        )

        figure = make_subplots(specs=[[{"secondary_y": True}]])

        figure.add_trace(
            go.Scatter(
                x=['SE'],
                y=['menções'],
                name='Menciones',
                marker={'color': 'rgb(51, 172, 255)'},
                text=df_grp.SE.map(lambda v: '{}'.format(str(v)[-2:])),
                hoverinfo='text',
                hovertemplate="Semana %{text} : %{y:.1f} Casos",
            ),
            secondary_y=True,
        )

        figure.add_trace(
            go.Scatter(
                x=['SE'],
                y=ks_cases,
                name='Casos',
                marker={'color': 'rgb(255,150,0)'},
                text=df_grp.SE.map(lambda v: '{}'.format(str(v)[-2:])),
                hoverinfo='text',
                hovertemplate="Semana %{text} : %{y:.1f} Casos",
            ),
            secondary_y=False,
        )

        figure.update_layout(
            title='Menções mídia social',
            xaxis=dict(
                title='Período (Ano/Semana)',
                tickangle=-60,
                nticks=len(ks_cases) // 4,
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
            ),
            yaxis=dict(
                title='Temperatura',
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(176, 196, 222)',
            ),
            showlegend=True,
            plot_bgcolor='rgb(255, 255, 255)',
            paper_bgcolor='rgb(245, 246, 249)',
            width=1100,
            height=500,
        )

        figure.update_yaxes(title_text="Y_axies", secondary_y=True)

        figure['layout']['legend'].update(
            x=-0.1,
            y=1.2,
            traceorder='normal',
            font=dict(family='sans-serif', size=12, color='#000'),
            bgcolor='#FFFFFF',
            bordercolor='#E2E2E2',
            borderwidth=1,
        )

        return figure.to_html()


class HomeCharts:
    colors = {
        'Ceará': 'rgb(0,0,0)',
        'Espírito Santo': 'rgb(255,0,0)',
        'Paraná': 'rgb(0,255,0)',
        'Minas Gerais': 'rgb(0,0,255)',
        'Rio de Janeiro': 'rgb(255,255,0)',
        'São Paulo': 'rgb(0,255,255)',
    }

    @classmethod
    def total_series(cls, case_series, disease):
        '''
        :param case_series:
        :param disease: dengue|chikungunya|zika
        :return:
        '''
        # gc = context['geocodigos'][0]
        series = (
            get_series_by_UF(disease)
            if disease not in case_series
            else case_series[disease]
        )

        if series.empty:
            return {
                'ufs': [],
                'start': None,
                'series': {},
                'series_est': {},
                'disease': disease,
            }

        ufs = list(set(series.uf.tolist()))
        # 51 weeks to get the end of the SE
        start = series.data.max() - timedelta(weeks=51)
        start = int(mktime(start.timetuple()))
        casos = {}
        casos_est = {}

        for uf in ufs:
            series_uf = series[series.uf == uf]
            datas = [
                int(mktime(d.timetuple())) * 1000 for d in series_uf.data[-52:]
            ]
            casos[uf] = [
                list(t)
                for t in zip(
                    datas, series_uf.casos_s[-52:].astype('int').tolist()
                )
            ]
            casos_est[uf] = [
                list(t)
                for t in zip(
                    datas, series_uf.casos_est_s[-52:].astype('int').tolist()
                )
            ]

        return {
            'ufs': ufs,
            'start': start,
            'series': casos,
            'series_est': casos_est,
            'disease': disease,
        }

    @classmethod
    def _create_chart(cls, case_series, disease):
        series_est = cls.total_series(case_series, disease=disease)[
            'series_est'
        ]

        dfs = []
        for k, v in series_est.items():
            df = pd.DataFrame(v)
            df.set_index(pd.to_datetime(df[0], unit='ms'), inplace=True)
            df.drop(columns=0, inplace=True)
            df.rename(columns={1: k}, inplace=True)
            df.index.name = None
            dfs.append(df)

        df_ufs = pd.concat(dfs, sort=True)

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        for k in df_ufs:
            fig.add_trace(
                go.Scatter(
                    x=df_ufs.index,
                    y=df_ufs[k],
                    name=k,
                    marker={'color': cls.colors[k]},
                    hovertemplate='%{x}<br>'
                    '%{y} Casos Estimados<br>'
                    '<extra></extra>',
                ),
                secondary_y=True,
            )

            fig.update_layout(
                height=350,
                width=1000,
                title_text="Casos estimados de {}".format(disease),
                plot_bgcolor='rgb(255, 255, 255)',
                paper_bgcolor='rgb(255, 255, 255)',
                showlegend=True,
                font=dict(family="sans-serif", size=14, color="black"),
                xaxis=dict(
                    # title='',
                    tickangle=-60,
                    nticks=len(df) // 3,
                    showline=True,
                    showgrid=True,
                    showticklabels=True,
                    linecolor='rgb(204, 204, 204)',
                    linewidth=0,
                    gridcolor='rgb(176, 196, 222)',
                    ticks='outside',
                    tickfont=dict(
                        family='Arial', size=12, color='rgb(82, 82, 82)'
                    ),
                ),
                yaxis=dict(
                    # title='',
                    showline=True,
                    showgrid=True,
                    showticklabels=True,
                    linecolor='rgb(204, 204, 204)',
                    linewidth=0,
                    gridcolor='rgb(176, 196, 222)',
                ),
            )

            fig.update_yaxes(
                title_text="Pessoas",
                secondary_y=True,
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='rgb(204, 204, 204)',
                linewidth=0,
                gridcolor='rgb(204, 204, 204)',
            )

        return fig.to_html()

    @classmethod
    def create_dengue_chart(cls, case_series):
        return cls._create_chart(case_series, 'dengue')

    @classmethod
    def create_chik_chart(cls, case_series):
        return cls._create_chart(case_series, 'chikungunya')

    @classmethod
    def create_zika_chart(cls, case_series):
        return cls._create_chart(case_series, 'zika')


class DashCharts:
    @classmethod
    def create_dash_chart_uf(cls):

        # Load data https://info.dengue.mat.br/...
        df_gender = pd.read_csv(
            'http://127.0.0.1:8000/api/notif_reduced?'
            'chart_type=age_gender&diseases=Dengue&state_abv=CE'
        )
        df_diseases = pd.read_csv(
            'http://127.0.0.1:8000/api/notif_reduced?'
            'chart_type=disease&diseases=Dengue&state_abv=CE'
        )

        all_options = {
            'Desease': ['Chikungunya', 'Dengue', 'Zika'],
            'Gênero': [u'Homens', 'Mulheres'],
        }

        data_gender = {
            'Homens': {'x': df_diseases.category, 'y': df_gender.Homem},
            'Mulheres': {'x': df_diseases.category, 'y': df_gender.Mulher},
        }

        data_age = {
            'Homens': go.Scatter(
                x=df_gender.category, y=df_gender.Homem, name='Homem'
            ),
            'Mulheres': go.Scatter(
                x=df_gender.category, y=df_gender.Mulher, name='Mulher'
            ),
        }

        # Start App
        app = DjangoDash('dash_app_state')

        app.layout = html.Div(
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P('Escolha uma doença:'),
                                    dcc.Checklist(
                                        id='Disease',
                                        value=['Homens'],
                                        labelStyle={'display': 'inline-block'},
                                    ),
                                ]
                            ),
                            html.Div(
                                [
                                    html.P('Escolha um Gênero:'),
                                    dcc.RadioItems(
                                        id='Gender',
                                        options=[
                                            {'label': k, 'value': k}
                                            for k in all_options.keys()
                                        ],
                                        value='All',
                                        labelStyle={'display': 'inline-block'},
                                    ),
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Graph(
                                        id='graph-gender',
                                        style={
                                            "height": "200px",
                                            "width": "50%",
                                        },
                                    )
                                ]
                            )
                        ]
                    ),
                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Graph(
                                        id='graph-age',
                                        style={
                                            "height": "200px",
                                            "width": "50%",
                                        },
                                    )
                                ]
                            )
                        ]
                    ),
                ]
            ),
            className='graph-app',
        )

        @app.callback(
            dash.dependencies.Output('Disease', 'options'),
            [dash.dependencies.Input('Gender', 'value')],
        )
        def set_disease_options(selected_Gender):
            return [
                {'label': i, 'value': i} for i in all_options[selected_Gender]
            ]

        @app.callback(
            dash.dependencies.Output('graph-gender', 'figure'),
            [dash.dependencies.Input('Disease', 'value')],
        )
        def update_graph_gender(selector):
            data = []
            for value in selector:
                data.append(
                    {
                        'x': data_gender[value]['x'],
                        'y': data_gender[value]['y'],
                        'type': 'bar',
                        'name': value,
                    }
                )
            figure = {
                'data': data,
                "layout": go.Layout(
                    title="Distribuição por Gênero",
                    yaxis={"title": "Casos"},
                    xaxis={"title": "Disease", "tickangle": 0},
                    margin={'l': 55, 'b': 70, 't': 50, 'r': 5},
                    font=dict(family='sans-serif', size=12, color='#000'),
                ),
            }
            return figure

        @app.callback(
            dash.dependencies.Output('graph-age', 'figure'),
            [dash.dependencies.Input('Disease', 'value')],
        )
        def update_graph_age(selector):
            data = []
            for value in selector:
                data.append(
                    {
                        'x': data_age[value]['x'],
                        'y': data_age[value]['y'],
                        'type': 'bar',
                        'name': value,
                    }
                )
            figure = {
                'data': data,
                "layout": go.Layout(
                    title="Distribuição por Idade",
                    yaxis={"title": "Casos"},
                    xaxis={"title": "Idade", "tickangle": 45},
                    barmode='stack',
                    margin={'l': 55, 'b': 70, 't': 50, 'r': 5},
                    font=dict(family='sans-serif', size=12, color='#000'),
                ),
            }
            return figure


class Dash_Epy:
    @classmethod
    def create_dash_epyweek_uf(cls):

        df_epyears = pd.read_csv(
            'http://127.0.0.1:8000/api/notif_reduced?'
            'chart_type=epiyears&diseases=Dengue&state_abv=CE'
        )

        trace0 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2010'], name='2010'
        )
        trace1 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2011'], name='2011'
        )
        trace2 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2012'], name='2012'
        )
        trace3 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2013'], name='2013'
        )
        trace4 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2014'], name='2014'
        )
        trace5 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2015'], name='2015'
        )
        trace6 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2016'], name='2016'
        )
        trace7 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2017'], name='2017'
        )
        trace8 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2018'], name='2018'
        )
        trace9 = go.Scatter(
            x=df_epyears['se_notif'], y=df_epyears['2019'], name='2019'
        )

        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        # app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        app = DjangoDash('app_epy', external_stylesheets=external_stylesheets)

        app.layout = html.Div(
            style={'height': '290vh'},
            children=[
                dcc.Graph(
                    id='graph_epy',
                    figure={
                        'data': [
                            trace0,
                            trace1,
                            trace2,
                            trace3,
                            trace4,
                            trace5,
                            trace6,
                            trace7,
                            trace8,
                            trace9,
                        ],
                        "layout": go.Layout(
                            title="Casos por semanas epidemiologicas",
                            yaxis={"title": "Casos"},
                            xaxis={"title": "Semana"},
                            showlegend=False,
                            # margin={'l': 35, 'b': 70, 't': 50, 'r': 5},
                            font=dict(
                                family='sans-serif', size=12, color='#000'
                            ),
                        ),
                    },
                    style={'height': 'inherit'},
                )
            ],
        )

        # return figure
