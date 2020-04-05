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
                html.Li(html.A('Hack the Crisis', href='/hack_the_crisis')),
            ])
        ])
    ]),
    html.A(href='#menu', className='navPanelToggle', children=html.Span(className='fa fa-bars')),

    # First section
    html.Section(id="main", className="wrapper", children=[
        html.Div(className="container", children=[
            html.Header(className="major special", children=[
                html.H2("Optimizing"),
                html.P("The problem")
            ]),

            html.P(children=[
                "According to ",
                html.A('Sveriges Radio ',
                       href='https://omni.se/iva-patienter-har-nu-borjat-flyttas-mellan-regionerna/a/50gb1O'),
                "regions have already started to reallocate patients and the Swedish government has given "
                "the national board of Health and Welfare (Socialstyrelsen) ",
                html.A('the mandate to also reallocate protective gears and other resources',
                       href='https://www.dn.se/nyheter/sverige/skyddsmaterial-ska-flyttas-mellan-regionerna-historiskt-beslut/'),
                " between the regions. "
                ]),

            # Link 1:
            # html.A("Sveriges Radio", href="https://omni.se/iva-patienter-har-nu-borjat-flyttas-mellan-regionerna/a/50gb1O"),
            # html.Br(),
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
                html.H2("Our optimization solution"),
                html.P("About"),
            ]),
            html.P("To showcase the broad range of possibilities, we have created an interactive optimization solution"
                   "for how many patients should be moved between different Swedish regions."),
            html.Header(className="major special", children=[
                html.P("User Guide"),
            ]),
            html.P("As a user, you get to define how the trade-off between different possible objections should be "
                   "handled. To make it simple, we have created a pre-defined list of four different criteria."
                   "You decide how important each criteria is by toggling the sliders below. "
                   "A value of 0 (all the way to the left) means that the solver will not care about that objective"
                   "when searching for an optimal solution, whereas a value of 10 (all the way to the right means "
                   "that the solver will optimize mainly to meet that criteria. The four criteria are:"),
            html.Ol(children=[
                html.Li(children=[html.Strong("Maximum Undercapacity"), " means blablabla"]),
                html.Li(children=[html.Strong("TILDA"), " HJÄLP"]),
                html.Li(children=[html.Strong("GÄRNA TILL"), " MED ATT"]),
                html.Li(children=[html.Strong("FYLLA I"), " DESSA"]),
            ]),
            html.Header(className="major special", children=[
                html.P("Try it out!"),
            ]),
            html.P("Delete margin here...")
        ]),
    ]),

    html.Div(style={'height': '800px', 'margin-top': '50px', 'margin-bottom': '50px'}, children=[
        html.Div(style={'width': '30%', 'display': 'inline-block', 'margin-left': '5%', 'margin-bottom': '5%'}, children=[
            html.H3('Set parameters'),
            html.Div(children=[
                dcc.Markdown('Absolute overcapacity'),
                dcc.Slider(
                    id='slider_w_overcap_abs',
                    min=0,
                    max=10,
                    step=0.1,
                    value=5,
                    marks={0: '0', 10: '10'}
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('Relative overcapacity'),
                dcc.Slider(
                    id='slider_w_overcap_rel',
                    min=0,
                    max=10,
                    step=0.1,
                    value=5,
                    marks={0: '0', 10: '10'}
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('Total number of transfers'),
                dcc.Slider(
                    id='slider_w_nb_trans',
                    min=0,
                    max=10,
                    step=0.1,
                    value=5,
                    marks={0: '0', 10: '10'}
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('Total length (km) of transfers'),
                dcc.Slider(
                    id='slider_w_km_trans',
                    min=0,
                    max=10,
                    step=0.1,
                    value=5,
                    marks={0: '0', 10: '10'}
                ),
            ]),

            html.Br(),
            dcc.Input(id="input_date", type="text", value='2020-04-03'),
            html.Br(),

            html.Div(html.Button('Run', n_clicks=0, id="button_run"), style={'text-align': 'center'}),
            html.Br(),

            dcc.Loading(
                id="loading",
                type="circle",
                children=' '
            ),
            html.Br(),
        ]),

        # TODO: Fix styling and positioning of buttons
        html.Div(style={'width': '50%', 'height': '100%', 'display': 'inline-block', 'margin-left': '10%'},
                 children=[
                     html.H3(id='map_title'),
                     html.Div(id='map_output', style={'height': '700px'}),
                     html.Div(style={'display': 'inline-block', 'text-align': 'center', 'position': 'relative', 'margin-left': '10%'},
                              children=[
                         html.Button('Current', n_clicks=0, id="button_map_current",
                                     style={'display': 'inline-block', 'margin': '20px 5px%', 'position': 'relative'}),
                         html.Button('Predicted', n_clicks=0, id="button_map_predicted",
                                     style={'display': 'inline-block', 'margin': '20px 5px', 'position': 'relative'}),
                         html.Button('Optimized', n_clicks=0, id="button_map_optimized",
                                     style={'display': 'inline-block', 'margin': '20px 5px', 'position': 'relative'}),
                     ])
                 ]),
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
    ]),

    # hiddens divs for storing maps
    html.Div(id='map_storing_current', style={'display': 'None'}),
    html.Div(id='map_storing_predicted', style={'display': 'None'}),
    html.Div(id='map_storing_optimized', style={'display': 'None'}),
])


@app.callback(
    [
        Output('map_storing_current', 'children'),
        Output('map_storing_predicted', 'children'),
        Output('map_storing_optimized', 'children'),
        Output('loading', 'children'),
    ],
    [
        Input('button_run', 'n_clicks'),
        Input('input_date', 'value')
    ],
    state=[
        State(component_id='slider_w_overcap_abs', component_property='value'),
        State(component_id='slider_w_overcap_rel', component_property='value'),
        State(component_id='slider_w_nb_trans', component_property='value'),
        State(component_id='slider_w_km_trans', component_property='value')
    ]
)
def update_map(nbr_run_clicks, date, w_overcap_abs, w_overcap_rel, w_nb_trans, w_km_trans):
    from src.optimization.main_optimization import run_optimization
    initial_map, final_map, final_map_wo_opt, allocation_plan = \
        run_optimization(
            w_overcap_abs=w_overcap_abs,
            w_overcap_rel=w_overcap_rel,
            w_nb_trans=w_nb_trans,
            w_km_trans=w_km_trans,
            start_day=date
        )

    print(allocation_plan)
    iframe_current = html.Iframe(srcDoc=initial_map.get_root().render(), width='100%', height='100%')
    iframe_predicted = html.Iframe(srcDoc=final_map_wo_opt.get_root().render(), width='100%', height='100%')
    iframe_optimized = html.Iframe(srcDoc=final_map.get_root().render(), width='100%', height='100%')

    value_to_loading = ''

    return iframe_current, iframe_predicted, iframe_optimized, value_to_loading


@app.callback(
    [
        Output('map_title', 'children'),
        Output('map_output', 'children'),
    ],
    [
        Input('button_map_current', 'n_clicks'),
        Input('button_map_predicted', 'n_clicks'),
        Input('button_map_optimized', 'n_clicks'),
        Input('map_storing_current', 'children'),
        Input('map_storing_predicted', 'children'),
        Input('map_storing_optimized', 'children'),
    ],
    state=[State(component_id='input_date', component_property='value')]
)
def update_map_output(btn_current, btn_predicted, btn_optimized,
                      iframe_current, iframe_predicted, iframe_optimized,
                      date
                      ):
    import datetime

    today = datetime.datetime.strptime(date, '%Y-%m-%d')
    forecasted_date = today + datetime.timedelta(days=3)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'button_map_current' in changed_id:
        map_title = f'Current state for {today.date()}'
        iframe_to_show = iframe_current

    elif 'button_map_predicted' in changed_id:
        map_title = f'Forecasted state for {forecasted_date.date()}'
        iframe_to_show = iframe_predicted

    elif 'button_map_optimized' in changed_id:
        map_title = f'Optimized state for {forecasted_date.date()}'
        iframe_to_show = iframe_optimized

    else:
        map_title = f'Current state for {today.date()}'
        iframe_to_show = iframe_current

    return map_title, iframe_to_show


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
    elif pathname == '/hack_the_crisis':
        return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("hack_the_crisis.html", "r").read()}'),
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
    #elif pathname == '/hack_the_crisis':
    #    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("hack_the_crisis.html", "r").read()}'),
    #elif pathname == '/optimizing':
    #    return layout_optimizing
    #else:
    #    return html.H1('404, this page does not exist!')
