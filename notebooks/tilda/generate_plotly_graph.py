import run_model
import create_input_data
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as po


def get_data():
	filepath = 'xgboost_input.csv'
	if not os.path.exists(filepath):
		create_input_data

	input_data = pd.read_csv('xgboost_input.csv')
	output_data, model = run_model.run_model()

	results = run_model.results(input_data, output_data)
	return results


def plot(results):
    regioner = list(results['Region'].unique())
    
    df = pd.read_csv("../../data/iva_kumulativ.csv",sep=";")
    df_T = df.T
    df_T.columns = df_T.iloc[0]
    df_T = df_T.drop(df_T.index[0])
    df_T = df_T.drop(columns=["Hela riket"])
    df_T = df_T.reset_index()
    df_T = df_T.rename(columns={"index": "date"})
    df_T = pd.melt(df_T, id_vars=["date"],var_name="Region",value_name="iva")
    temp = df_T.merge(results,on=["date","Region"],how="left")
    
    line = go.Scatter(
	    x=results[results['Region'] == regioner[0]]['date'],
	    y=results[results['Region'] == regioner[0]]['predicted'],
	    name='Predicted IVA'
	)
    
    line2 = go.Scatter(
	    x=results[results['Region'] == regioner[0]]['date'],
	    y=results[results['Region'] == regioner[0]]['iva'],
	    name='Actual IVA'
	)
    
    updatemenus = [
	    {
	        'buttons': [
	            {
	                'method': 'restyle',
	                'label': region,
	                'args': [
	                    {'x': [results[results['Region'] == region]['date']], 
	                     'y': [results[results['Region'] == region]['predicted'], 
	                           results[results['Region'] == region]['iva']
	                          ]
	                    },
	                ]
	            } for region in regioner
	            
	            
	        ],
	        'direction': 'down',
	        'showactive': True,
	    }
	]
    
    layout = go.Layout(
	    updatemenus=updatemenus,
	)
    
    figure = go.Figure(data=[line, line2],  layout=layout)
    figure.update_layout(
	    xaxis_tickformat='%d %B',
	)
    figure.write_html('./plotly_graph.html')


if __name__=='__main__':
	results = get_data()
	plot(results)
