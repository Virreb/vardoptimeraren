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

    #First scetion
    html.Section(id="main", className="wrapper", children=[
        html.Div(className="container", children=[
            html.Header(className="major special", children=[
                html.H2("Optimizing"),
                html.P("The problem")
            ]),
            html.P("According to <a href=” https://omni.se/iva-patienter-har-nu-borjat-flyttas-mellan-regionerna/a/50gb1O”>Sveriges Radio</a>, "
                   "regions have already started to reallocate patients and the Swedish government has given "
                   "the national board of Health and Welfare (Socialstyrelsen) "
                   "<a href=” https://www.dn.se/nyheter/sverige/skyddsmaterial-ska-flyttas-mellan-regionerna-historiskt-beslut/ “> "
                   "the mandate to also reallocate protective gears and other resources</a> between the regions. "),

            #Link 1:
            #html.A("Sveriges Radio", href="https://omni.se/iva-patienter-har-nu-borjat-flyttas-mellan-regionerna/a/50gb1O"),
            #html.Br(),
            html.P("Even with perfect information about the future spread of the disease, planning how this reallocation "
                   "should be pursued is far from trivial. Many different kinds of resources may need to be moved and "
                   "different objectives will need to be weighed against each other (e.g. overcapacity vs. cost for "
                   "logistics) while boundary conditions remain intact (e.g. a region can’t treat more patients than "
                   "its maximum capacity)."),
            html.Header(className="major special", children=[
                html.P("The Solution"),
            ]),
            html.P("Luckily, there is a good solution for this type of complex, multi-objective problems. "
                   "In comes mathematical decision optimization!"),
            html.P("Decision optimization is a set of frameworks for finding the mathematically optimal solutions for a "
                   "wide range of different problems within sectors ranging from manufacturing and logistics to finance "
                   "and telecom. The interested reader can find a more thorough explanation in "
                   "<a href=”https://www.advectas.com/en/blog/what-is-decision-optimisation-and-how-can-it-generate-commercial-value/”>this</a>"
                   " blog post from our awesome team member Tilda Lundgren."
                   "Suffice it to say here that decision optimization is typically done in four stages:"),
            html.Ol(children=[
                html.Li("The problem is formulated mathematically"),
                html.Li("An objective function is formulated. In reality, this often means deciding how to weigh different objectives against each other. "),
                html.Li("Boundary conditions are formulated (No region can have less than 0 patients, ..?HELP TILDA)"),
                html.Li("A large subset of the possible solution space is tested and the optimization engine "
                        "converges on an optimal solution."),
            ]),
            html.P("Our optimization solution uses our <a href=”forecast.html>forecasts</a> of the number of ICU-cases "
                   "in each region to optimize how many patients should be moved between the different regions. "
                   "The user inputs to what extent different possible objectives (e.g. maximizing overcapacity in the "
                   "healthcare system vs. minimizing long patient transports) should be considered. "),
            html.Header(className="major special", children=[
                html.P("The Technology"),
            ]),
            html.P("The solution was built in python using the optimization engine "
                   "<a href=” https://www.ibm.com/se-en/analytics/cplex-optimizer”>IBM CPLEX</a> and visualized through "
                   "the open source plotting library <a href=” https://python-visualization.github.io/folium/”>"
                   "Folium</a>. Together with the forecasting solution, it was isolated in a "
                   "<a href=” https://www.docker.com/why-docker”>Docker container</a> and deployed on Microsoft Azure. "),
            html.Header(className="major special", children=[
                html.H2("Try our optimization solution"),
                html.P("About"),
            ]),
            html.P("To showcase the broad range of possibilities, we have created an interactive optimization solution"
                   "for how many patients should be moved between different Swedish regions."),
            html.Header(className="major special", children=[
                html.P("User Guide"),
            ]),
            html.P("As a user, you get to define how the trade-off between different possible objections should be "
                   "handled. To make it simple, we have created a pre-defined list of four different criteria."
                   "As a user, you get to decide how important each criteria is by toggling the sliders below. "
                   "A value of 0 (all the way to the left) means that the solver will not care about that objective"
                   "when searching for an optimal solution, whereas a value of 10 (all the way to the right means "
                   "that the solver will optimize mainly to meet that criteria. The four criteria are:"),
            html.Ol(children=[
                html.Li(children=[html.Strong("Maximum Undercapacity"), " means blablabla"]),
                html.Li(children=[html.Strong("TILDA"), " HJÄLP"]),
                html.Li(children=[html.Strong("GÄRNA TILL"), " MED ATT"]),
                html.Li(children=[html.Strong("FYLLA I"), " DESSA"]),
            ])

        ]),
    ]),

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

    #if pathname == '/':
    #    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("src/webapp/index.html", "r").read()}'),
    #elif pathname == '/forecasting':
    #    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("src/webapp/forecast.html", "r").read()}'),
    #elif pathname == '/about':
    #    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("src/webapp/about.html", "r").read()}'),
    #elif pathname == '/optimizing':
    #    return layout_optimizing
    #else:
    #    return html.H1('404, this page does not exist!')
