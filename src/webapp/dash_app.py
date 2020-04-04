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
    # Not sure if this block is needed
    # html.Header(children=[
    #     html.Title('Vårdoptimeraren'),
    #     html.Meta(name='viewport', charSet='utf-8', content='width=device-width initial-scale=1'),
    #     html.Link(rel='stylesheet', href='assets/main.css'),
    # ]),

    html.Header(id='header', children=[
        html.H1(children=[
            html.Strong(html.A('Vårdoptimeraren', href='/')),
            ' by Team Advectas'
        ]),
        html.Nav(id='nav', children=[
            html.Ul(children=[
                html.Li(html.A('Home', href='/')),
                html.Li(html.A('Forecasting', href='/forecasting')),
                html.Li(html.A('Optimizing', href='/optimizing')),
            ])
        ])
    ]),
    html.A(href='#menu', className='navPanelToggle', children=html.Span(className='fa fa-bars')),

    html.Div(style={'height': '800px', 'margin-top': '50px', 'margin-bottom': '50px'}, children=[
        html.Div(style={'width': '30%', 'display': 'inline-block', 'margin-left': '5%', 'margin-bottom': '5%'}, children=[
            html.H3('Set parameters'),
            html.Div(children=[
                dcc.Markdown('w_max_under'),
                dcc.Slider(
                    id='wmax_under',
                    min=0,
                    max=200,
                    step=0.5,
                    value=100,
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('w_max_over'),
                dcc.Slider(
                    id='wmax_over',
                    min=0,
                    max=20,
                    step=0.5,
                    value=1,
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('w_total_undercapacity'),
                dcc.Slider(
                    id='w_total_undercapacity',
                    min=0,
                    max=200,
                    step=0.5,
                    value=100,
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('w_nb_long_transfers'),
                dcc.Slider(
                    id='w_nb_long_transfers',
                    min=0,
                    max=1,
                    step=0.1,
                    value=0.01,
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('w_km_patient_transfers'),
                dcc.Slider(
                    id='w_km_patient_transfers',
                    min=0,
                    max=1,
                    step=0.1,
                    value=0.01,
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('w_nb_patient_transfers'),
                dcc.Slider(
                    id='w_nb_patient_transfers',
                    min=0,
                    max=10,
                    step=0.5,
                    value=1,
                ),
            ]),
            html.Div(style={'text-align': 'center'}, children=[
                dcc.Loading(    # TODO: loading does not work :(
                    id="loading",
                    type="circle",
                    children=html.Button('Kör', n_clicks=0, id="optimize_button"),
                ),
            ]),
            html.Br()
        ]),

        html.Div(id='map_output', style={'width': '50%',
                                         'height': '100%',
                                         'display': 'inline-block',
                                         'margin-left': '10%'
                                         }),

    ]),

    html.Footer(id='footer', children=[
        html.Div(className='container', children=[
            html.Ul(className='icons', children=[
                html.A(href='http://www.advectas.com',
                       children=html.Img(
                            src=app.get_asset_url('advectas_logo_cg_black.png'),
                            alt="Advectas logo", width='300px')
                       )
            ]),
            html.Ul(className='copyright', children=[
                html.Li('© Advectas 2020'),
                html.Li(children=[
                    'Design: ',
                    html.A('TEMPLATED', href='http://templated.co')
                ]),
            ])
        ])
    ])
])


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
def update_map(nbr_clicks, wmax_under, wmax_over, w_total_undercapacity, w_nb_patient_transfers, w_km_patient_transfers,
               w_nb_long_transfers):
    from src.optimization.main_optimization import run_optimization

    initial_map, final_map, allocation_plan = run_optimization(w_max_under=wmax_under, w_max_over=wmax_over,
                                                               w_total_undercapacity=w_total_undercapacity,
                                                               w_nb_patient_transfers=w_nb_patient_transfers,
                                                               w_km_patient_transfers=w_km_patient_transfers,
                                                               w_nb_long_transfers=w_nb_long_transfers)

    print(allocation_plan)
    html_string = final_map.get_root().render()

    return html.Iframe(srcDoc=html_string, width='100%', height='100%')


# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):

    # use the first list of ifs when running from WSGI
    if pathname == '/':
        return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("index.html", "r").read()}'),
    elif pathname == '/forecasting':
        return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("forecast.html", "r").read()}'),
    elif pathname == '/about':
        return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("about.html", "r").read()}'),
    elif pathname == '/optimizing':
        return layout_optimizing
    else:
        return html.H1('404, this page does not exist!')

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
