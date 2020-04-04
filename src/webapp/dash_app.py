# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
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

    html.Button("Kör", n_clicks=0, id="optimize_button"),

    html.Div(children=[
        dcc.Markdown('Sätt parameter w_max_under'),
        dcc.Slider(
            id='wmax_under',
            min=0,
            max=200,
            step=0.5,
            value=100,
            #marks={0: "0", 10: "10", 20: "20"},
        ),
    ]),

    html.Div(children=[
        dcc.Markdown('Sätt parameter w_max_over'),
        dcc.Slider(
            id='wmax_over',
            min=0,
            max=20,
            step=0.5,
            value=1,
            # marks={0: "0", 10: "10", 20: "20"},
        ),
    ]),

    html.Div(children=[
        dcc.Markdown('Sätt parameter w_total_undercapacity'),
        dcc.Slider(
            id='w_total_undercapacity',
            min=0,
            max=200,
            step=0.5,
            value=100,
            #marks={0: "0", 10: "10", 20: "20"},
        ),
    ]),

    html.Div(children=[
        dcc.Markdown('Sätt parameter w_nb_long_transgers'),
        dcc.Slider(
            id='w_nb_long_transfers',
            min=0,
            max=1,
            step=0.1,
            value=0.01,
            #marks={0: "0", 10: "10", 20: "20"},
        ),
    ]),

    html.Div(children=[
        dcc.Markdown('Sätt parameter w_km_patient_transfers'),
        dcc.Slider(
            id='w_km_patient_transfers',
            min=0,
            max=1,
            step=0.1,
            value=0.01,
            #marks={0: "0", 10: "10", 20: "20"},
        ),
    ]),

    html.Div(children=[
        dcc.Markdown('Sätt parameter w_nb_patient_transfers'),
        dcc.Slider(
            id='w_nb_patient_transfers',
            min=0,
            max=10,
            step=0.5,
            value=1,
            #marks={0: "0", 10: "10", 20: "20"},
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
    [Input('wmax_under', 'value')])
def update_slider_output(value):
    import time
    time.sleep(1)
    return f'Du valde {value} änna gubben!'


@app.callback(
    Output('map_output', 'children'),
    [Input('optimize_button', 'n_clicks')],
    state=[State(component_id='wmax_under', component_property='value'),
           State(component_id='wmax_over', component_property='value'),
           State(component_id='w_total_undercapacity', component_property='value'),
           State(component_id='w_nb_patient_transfers', component_property='value'),
           State(component_id='w_km_patient_transfers', component_property='value'),
           State(component_id='w_nb_long_transfers', component_property='value')]
)

def update_map(value, wmax_under, wmax_over, w_total_undercapacity, w_nb_patient_transfers, w_km_patient_transfers,
               w_nb_long_transfers):
    import folium
    import numpy as np
    from src.optimization.main_optimization import run_optimization

    random_location = [45, 10] + np.random.randn(2)*5

    # create sample map
    m = folium.Map(
        location=random_location,
        zoom_start=5,
        tiles='Stamen Terrain'
    )

    initial_map, final_map, allocation_plan = run_optimization(w_max_under=wmax_under, w_max_over=wmax_over,
                                                               w_total_undercapacity=w_total_undercapacity,
                                                               w_nb_patient_transfers=w_nb_patient_transfers,
                                                               w_km_patient_transfers=w_km_patient_transfers,
                                                               w_nb_long_transfers=w_nb_long_transfers)

    print(allocation_plan)
    tooltip = 'Click me!'
    folium.Marker(random_location, popup=value, tooltip=tooltip).add_to(m)
    html_string = final_map.get_root().render()

    return html.Iframe(srcDoc=html_string, width='100%', height='500px')


# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):

    # use the first list if running from WSGI, the other if in prod
    # if pathname == '/':
    #     return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("index.html", "r").read()}'),
    # elif pathname == '/forecasting':
    #     return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("forecast.html", "r").read()}'),
    # elif pathname == '/about':
    #     return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("about.html", "r").read()}'),
    # elif pathname == '/optimizing':
    #     return layout_optimizing
    # else:
    #     return html.H1('404, this page does not exist!')

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
