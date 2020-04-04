# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import flask

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
# app = dash.Dash(__name__, server=server, url_base_pathname='/optimization/', external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__, server=server, url_base_pathname='/optimization/', assets_folder='assets2')
app = dash.Dash(__name__, server=server, assets_folder='assets2')

# app.config.suppress_callback_exceptions = True
# app.layout = html.Div([
#     dcc.Location(id='url', refresh=False),
#     html.Div(id='page-content')
# ])

app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    html.H1(children='AI-Mackapären 5000'),
    html.Br(),
    html.H3(children='''
        Developed by Advectas during Hack the crisis 2020.
    '''),

    html.Div(children=[
        dcc.Slider(
            id='slider_1',
            min=0,
            max=20,
            step=0.5,
            value=10,
            marks={0: "0", 10: "10", 20: "20"},
        ),
    ]),

   # dcc.Graph(
   #     id='example-graph',
   #     figure={
   #         'data': [
   #             {'x': ['VB', 'Fredvall'], 'y': [6, 1], 'type': 'bar'},
   #         ],
   #         'layout': {
   #             'title': 'Antal timmar i Windows i snitt per dag'
   #         }
   #     }
   # ),

    html.Div(id='map_output', children=''),

    dcc.Loading(
        id="loading-2",
        children=html.Div(id="slider_1_output"),     # change place of this too visualize loading
        type="circle",
    ),

    html.Img(src=app.get_asset_url('banner.jpg')),
    print(app.get_asset_url('banner.jpg'))
])


@server.route('/')
def render_index_page():
    return flask.send_file('index.html')


@server.route('/forecast')
def render_forecast_page():
    return flask.send_file('forecast.html')


@server.route('/about')
def render_about_page():
    return flask.send_file('about.html')


@app.callback(
    Output('slider_1_output', 'children'),
    [Input('slider_1', 'value')])
def update_slider_output(value):
    import time
    time.sleep(1)
    return f'Du valde {value} änna gubben!'


@app.callback(
    Output('map_output', 'children'),
    [Input('slider_1', 'value')])
def update_map(value):
    import folium
    import numpy as np

    random_location = [45, 10] + np.random.randn(2)*5

    m = folium.Map(
        location=random_location,
        zoom_start=5,
        tiles='Stamen Terrain'
    )

    tooltip = 'Click me!'
    folium.Marker(random_location, popup=value, tooltip=tooltip).add_to(m)
    html_string = m.get_root().render()

    return html.Iframe(srcDoc=html_string, width='100%', height='500px')


# Update the index
# @app.callback(dash.dependencies.Output('page-content', 'children'),
#               [dash.dependencies.Input('url', 'pathname')])
# def display_page(pathname):
#     if pathname == '/forecasting':
#         return 'Hej'
#     elif pathname == '/optimization':
#         return layout_optimization
#     else:
#         # layout_index = html.Iframe(id='index', srcDoc=open('index.html', 'r').read(), width='100%', height='100%'),
#         layout_index = html.Div(open('index.html', 'r').read())
#         # return flask.send_file('index.html')
#         return layout_index
#
#         # You could also return a 404 "URL not found" page here
