# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import flask
import dash_dangerously_set_inner_html
from src.forecast import plotly_create_html

server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server, assets_folder='assets')
app.config.suppress_callback_exceptions = True  # for multi pages

# This is a placeholder for the content, which is filled depending on what URL you're on
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

app.title = 'Vårdoptimeraren'

# TODO: Update this
DATE = '2020-04-03'
forecast_figure = plotly_create_html.main()

layout_optimizing = html.Div(children=[

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

    #FIRST Section
    html.Section(id="main", className="wrapper", children=[
        html.Div(className="container", children=[
            html.Header(className="major special", children=[
                html.H2("Our optimization solution"),
                html.P("About"),
            ]),
            html.P("To showcase the broad range of possibilities within decision optimization, we have created an interactive optimization solution"
                       " for how many patients should be moved between different Swedish regions. The optimizer will "
                       "take your input in consideration and search for the optimal solution. Information about decision optimization can be found below."),
            html.Header(className="major special", children=[
                html.P("User Guide"),
            ]),
            html.P("As a user, you get to define how the trade-off between different possible objections should be "
                   "handled. To make it simple, we have created a pre-defined list of four different criteria."
                   "You decide how important each criteria is by toggling the sliders below. "
                   "A value of 0 (all the way to the left) means that the solver will not care about that objective "
                   "when searching for an optimal solution, whereas a value of 10 (all the way to the right means "
                   "that the solver will optimize mainly to meet that criteria. The four criteria are:"),
            html.Ol(children=[
                html.Li(children=[html.Strong("Even distribution of absolute capacity"),
                                  " means that the optimization engine tries to find a solution where absolute surplus capacity is evenly distribution among regions."]),
                html.Li(children=[html.Strong("Even distribution of relative capacity"),
                                  " means that the optimization engine tries to find a solution where relative surplus capacity is evenly distribution among regions."]),
                html.Li(children=[html.Strong("Minimizing the number of patient transfers"),
                                  " means that the optimization engine tries to find a solution where the number of patients that are transferred is minimized."]),
                html.Li(children=[html.Strong("Minimizing the total sum of transfer kilometers"),
                                  " means that the optimization engine tries to find a solution where the total sum of transfer kilometers is minimized."]),
            ]),
        ]),

    ]),

    #NEW
    html.Section(id="main", className="wrapper", children=[
        html.Div(style={'height': '800px', 'margin-bottom': '50px'}, children=[
        html.Div(style={'width': '30%', 'display': 'inline-block', 'margin-left': '5%', 'margin-bottom': '1%'}, children=[
            html.H3('Set parameters'),
            html.Div(children=[
                dcc.Markdown('Even distribution of undercapacity'),
                dcc.Slider(
                    id='slider_w_undercap',
                    min=0,
                    max=10,
                    step=0.1,
                    value=1,
                    marks={0: '0', 10: '10'}
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('Even distribution of overcapacity'),
                dcc.Slider(
                    id='slider_w_overcap',
                    min=0,
                    max=10,
                    step=0.1,
                    value=1,
                    marks={0: '0', 10: '10'}
                ),
            ]),

            html.Div(children=[
                dcc.Markdown('Total number of patient transfers'),
                dcc.Slider(
                    id='slider_w_nb_trans',
                    min=0,
                    max=10,
                    step=0.1,
                    value=1,
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
                    value=1,
                    marks={0: '0', 10: '10'}
                ),
            ]),

            # html.Br(),
            # dcc.Input(id="input_date", type="text", value='2020-04-03'),
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
                     html.Div(id='map_output', style={'height': '700px'}),
                     html.Div(style={'display': 'inline-block', 'text-align': 'center', 'position': 'relative', 'margin-left': '7%'},
                              children=[
                         html.Button('Show current state', n_clicks=0, id="button_map_current",
                                     style={'display': 'inline-block',
                                            'margin': '20px 5px%',
                                            'position': 'relative',
                                            'font-size': '10px'}
                                     ),
                         html.Button('Show forecasted state', n_clicks=0, id="button_map_predicted",
                                     style={'display': 'inline-block',
                                            'margin': '20px 5px',
                                            'position': 'relative',
                                            'font-size': '10px'}
                                     ),
                         html.Button('Show suggested moves', n_clicks=0, id="button_map_optimized",
                                     style={'display': 'inline-block',
                                            'margin': '20px 5px',
                                            'position': 'relative',
                                            'font-size': '10px'}
                                     ),
                     ])
                 ]),
        ]),
    ]),

    # Second section
    html.Section(id="main", className="wrapper", children=[
        html.Div(className="container", children=[
            html.Header(className="major special", children=[
                html.H2("About Optimizing"),
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
            html.P(children=[
                "Decision optimization is a set of frameworks for finding the mathematically optimal solutions for a "
                   "wide range of different problems within sectors ranging from manufacturing and logistics to finance "
                   "and telecom. The interested reader can find a more thorough explanation in ",
                html.A(' this ',
                       href='https://www.advectas.com/en/blog/what-is-decision-optimisation-and-how-can-it-generate-commercial-value/'),
                " blog post from our awesome team member Tilda Lundgren. ",
               "Suffice it to say here that decision optimization is typically done in four stages:",
                ]),

            html.Ol(children=[
                html.Li("The problem is formulated mathematically"),
                html.Li("An objective function is formulated. In reality, this often means deciding how to weigh different objectives against each other. "),
                html.Li("Boundary conditions are formulated (e.g. no region can have less than 0 patients, and nor can 1.367 patients be sent from one "
			"region to another but the solution has to be integer-valued)."),
                html.Li("A large subset of the feasible solution space is tested and the optimization engine "
                        "converges on an optimal solution."),
            ]),

            html.P(children=[
                "Our optimization solution uses our ",
                html.A("forecasts", href='/forecasting'),
                " of the number of ICU-cases "
               "in each region to optimize how many patients should be moved between the different regions. "
               "The user inputs to what extent different possible objectives (e.g. maximizing overcapacity in the "
               "healthcare system vs. minimizing long patient transports) should be considered. ",
            ]),

            html.Header(className="major special", children=[
                html.P("The Technology"),
            ]),
            html.P(children=[
                "The solution shown here was built in python using the optimization engine ",
                html.A("IBM CPLEX", href="https://www.ibm.com/se-en/analytics/cplex-optimizer"),
                ", but we have also created a solution using the open source optimization API ",
                html.A("PuLP", href="https://coin-or.github.io/pulp/"),
                ". This way, the solution is truly open source and engine-independent.",
                " The solution is visualized through the open source plotting library ",
                html.A("Folium", href="https://python-visualization.github.io/folium/"),
                ". Together with the forecasting solution, it was isolated in a ",
                html.A("Docker", href="https://www.docker.com/why-docker"),
                " container and deployed on Microsoft Azure App Service."
            ]),


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

layout_forecasting = html.Div(children=[
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
                html.H2("Our Forecasts"),
                html.P("Number of needed ICU beds for COVID-19 patients, per region")
            ]),
            html.P("We have created machine learning models for forecasting the number of needed ICU beds for COVID-19 patients in all Swedish regions."),
            html.P("Please note that since we have found no publically available data about how many ICU beds are occupied in the different regions, "
                   " these forecasts depend on assumptions regarding how long the patients stay in the ICU. If some numbers"
                   " look unintuitive, this is likely the reason."),
            dcc.Graph(figure=forecast_figure),
            html.Header(className="major special", children=[
                html.H2("About Forecasting"),
            ]),
            html.Blockquote('- "The most important part is that the healthcare system gets access to numbers of '
                            'how many will need intensive care treatment or similar."'),
            html.P(children=[
                "Anders Tegnell, Swedish State Epidemiologist, ",
                html.A("to TT, April 4th 2020", href="https://omni.se/tegnell-prognoser-om-doda-ar-inte-det-viktigaste-for-oss/a/1n9jye"),
            ]),

            html.Header(className="major special", children=[
                html.P("The Problem"),

            ]),
            html.P('One of the main obstacles for facing the ongoing epidemic is the large amount of uncertainty '
                   'associated with its progress. In order to coordinate and plan our response, we need to know how '
                   'the disease will spread through society. We have used artificial intelligence and machine learning '
                   'to be one step ahead of the curve so we can proactively redirect our resources to where they will '
                   'be needed the most. '),

            html.Header(className="major special", children=[
                html.P("The Solution"),
            ]),
            html.P("We have forecasted the number of ICU-beds that will be occupied by COVID-19 patients in each "
                   "Swedish region over the next 3 days. Historic data about the number of new ICU-cases each day "
                   "is available at Svenska Intensivvårdsregistret (SIR). Additionally, we have used demographic data "
                   "for each region to improve the forecasts, since age and population are important factors for "
                   "determining the spread of the epidemic."),

            html.P("Different measures can be used as proxies for how fast the disease is spreading in the society. "
                   "Many of these are associated with problems that make them unsuitable for forecasting. For instance, "
                   "the number of confirmed COVID-19 cases depends on the testing strategy employed by a country, "
                   "and Sweden is currently in the process of changing its testing strategy. This will likely make "
                   "historic data about the number of confirmed cases unsuitable for predicting the future number of "
                   "confirmed cases. The number of confirmed deaths due to COVID-19 would likely be a more reliable "
                   "measure, but with only 391 dead across Sweden’s 21 regions, the amount of data is insufficient "
                   "for creating reliable forecasts for each individual region. We believe that the number of "
                   "ICU-beds that will be occupied by COVID-19 patients is a key measure which has more data points "
                   "available than the number of deaths, while still being robust to other error sources such as "
                   "differences in testing strategy."),
            html.P("As Anders Tegnell alluded to above, knowing the amount of needed ICU-beds for each region is "
                   "key for planning important resources such as how many doctors and nurses will need to work and "
                   "how much protective gear will be needed. It can also serve as vital information when planning and "
                   "optimizing which patients should be given treatment at which hospital and whether or not patients "
                   "should be moved across regional boundaries."),
            html.Header(className="major special", children=[
                html.P("The Technology"),
            ]),
            html.P(children=["A time series is a series of data points listed in time order. Time series forecasting comprises "
                   "methods for forecasting future values based on previously observed values. This can be done using "
                   "many different statistical models. We have used the widely popular ",
                html.A("XGBoost", href="https://xgboost.readthedocs.io/en/latest/"),
                   " framework which is based on a gradient boosted tree model. The solution is implemented in python and visualized "
                   "through the open source python framework ",
                    html.A("Plotly", href="https://plotly.com/graphing-libraries/"),
                    ".",
            ]),

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
    ])
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
    ],
    state=[
        State(component_id='slider_w_undercap', component_property='value'),
        State(component_id='slider_w_overcap', component_property='value'),
        State(component_id='slider_w_nb_trans', component_property='value'),
        State(component_id='slider_w_km_trans', component_property='value')
    ]
)
def update_maps(nbr_run_clicks, w_undercap, w_overcap, w_nb_trans, w_km_trans):
    from src.optimization.main_optimization import run_optimization

    initial_map, final_map, final_map_wo_opt, allocation_plan = \
        run_optimization(
            w_undercap=w_undercap,
            w_overcap=w_overcap,
            w_nb_trans=w_nb_trans,
            w_km_trans=w_km_trans,
            start_day=DATE
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
        Input('button_run', 'n_clicks'),
        Input('button_map_current', 'n_clicks'),
        Input('button_map_predicted', 'n_clicks'),
        Input('button_map_optimized', 'n_clicks'),
        Input('map_storing_current', 'children'),
        Input('map_storing_predicted', 'children'),
        Input('map_storing_optimized', 'children'),
    ],
)
def update_map_output(btn_run, btn_current, btn_predicted, btn_optimized,
                      iframe_current, iframe_predicted, iframe_optimized):
    import datetime

    today = datetime.datetime.strptime(DATE, '%Y-%m-%d')
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

    elif 'button_run' in changed_id:
        map_title = f'Optimized state for {forecasted_date.date()}'
        iframe_to_show = iframe_optimized

    else:
        map_title = f'Optimized state for {forecasted_date.date()}'
        iframe_to_show = iframe_optimized

    return map_title, iframe_to_show


# Update the index
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):

     #use the first list of ifs when running from WSGI
     if pathname == '/':
         return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("index.html", "r").read()}'),
     elif pathname == '/forecasting':
         return layout_forecasting
     elif pathname == '/hack_the_crisis':
         return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("hack_the_crisis.html", "r").read()}'),
     elif pathname == '/optimizing':
         return layout_optimizing
     else:
         return html.H1('404, this page does not exist!')

    #if pathname == '/':
    #    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("src/webapp/index.html", "r").read()}'),
    #elif pathname == '/forecasting':
    #    return layout_forecasting
    #elif pathname == '/hack_the_crisis':
    #    return dash_dangerously_set_inner_html.DangerouslySetInnerHTML(f'{open("src/webapp/hack_the_crisis.html", "r").read()}'),
    #elif pathname == '/optimizing':
    #    return layout_optimizing
    #else:
    #    return html.H1('404, this page does not exist!')

