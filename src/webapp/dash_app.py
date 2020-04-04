# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import flask
import dash_dangerously_set_inner_html

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, assets_folder='assets')
app.config.suppress_callback_exceptions = True  # for multi pages

# This is a placeholder for the content, which is filled depending on what URL you're on
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

layout_optimizing = html.Div(children=[
    # insert header and children from index.html but with dash html components
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

    html.Div(id='map_output', children=''),

    # wrap content with this to show blue circle to indicate loading, maybe the map final map?
    dcc.Loading(
        id="loading-2",
        children=html.Div(id="slider_1_output"),     # change place of this too visualize loading
        type="circle",
    ),

    html.Img(src=app.get_asset_url('banner.jpg')),
    # print(app.get_asset_url('banner.jpg'))  # debugging
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

    # create sample map
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
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("src/webapp/index.html", "r").read()}'),
    elif pathname == '/forecasting':
        return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("src/webapp/forecast.html", "r").read()}'),
    elif pathname == '/about':
        return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("src/webapp/about.html", "r").read()}'),
    elif pathname == '/optimizing':
        return layout_optimizing
    else:
        return html.H1('404, this page does not exist!')
