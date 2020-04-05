def main():
	import pandas as pd
	import math

	import plotly.graph_objects as go
	import plotly.offline as po

	df = pd.read_csv('../../src/forecast/plotly_data.csv')
	df = df.rename(columns={'iva_corrected': 'iva'})
	df['value'] = [df.iva.iloc[i] if not math.isnan(df.iva.iloc[i]) else df.predicted.iloc[i] for i in range(0, df.shape[0])]
	df['color'] = ['#FE465B' if not math.isnan(df.iva.iloc[i]) else '#7DDCDC' for i in range(0, df.shape[0])]
	df['name'] = ['prediction' if not math.isnan(df.iva.iloc[i]) else 'actual' for i in range(0, df.shape[0])]


	regioner = list(df['Region'].unique())

	line = go.Bar(
	    x=df[df['Region'] == regioner[0]]['date'],
	    y=df[df['Region'] == regioner[0]]['value'],
	    #name=df[df['Region'] == regioner[0]]['name'],
	    #marker={'color': 'red'}
	    marker={'color': df[df['Region'] == regioner[0]]['color']}
	)

	updatemenus = [
	    {
	        'buttons': [
	            {
	                'method': 'restyle',
	                'label': region,
	                'args': [
	                    {'x': [df[df['Region'] == region]['date']], 
	                     'y': [df[df['Region'] == region]['value'],
	                           #df[df['Region'] == region]['iva']
	                          ],
	                     'color': df[df['Region'] == region]['color']
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


	figure = go.Figure(data=[line],  layout=layout)
	figure.update_layout(
	    xaxis_tickformat='%d %B',
	    #showlegend=True
	)
	figure.write_html('../../plotly_graph.html')


if __name__ == '__main__':
	main()