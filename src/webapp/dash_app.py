# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import flask

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
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
])


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
