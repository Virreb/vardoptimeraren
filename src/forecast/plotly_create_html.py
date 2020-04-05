def main():
	import pandas as pd
	import math

	import plotly.graph_objects as go
	import plotly.offline as po

	df = pd.read_csv('../forecast/plotly_data.csv')
	df = df.rename(columns={'iva_corrected': 'iva'})
	df['value'] = [df.iva.iloc[i] if not math.isnan(df.iva.iloc[i]) else df.predicted.iloc[i] for i in range(0, df.shape[0])]
	df['color'] = ['#7DDCDC' if not math.isnan(df.iva.iloc[i]) else '#FE465B' for i in range(0, df.shape[0])]
	df['name'] = ['prediction' if not math.isnan(df.iva.iloc[i]) else 'actual' for i in range(0, df.shape[0])]


	regioner = list(df['Region'].unique())

	line = go.Bar(
	    x=df[df['Region'] == regioner[0]]['date'],
	    y=df[df['Region'] == regioner[0]]['value'],
	    #name=df[df['Region'] == regioner[0]]['name'],
	    #marker={'color': 'red'}
	    marker={'color': df[df['Region'] == regioner[0]]['color']},
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
	    title=go.layout.Title(
	       text='Number of active ICU patients (blue=actual, red=prediction)',
	        font=dict(size=18)
	    ),
	    
	    xaxis=go.layout.XAxis(
	        title=go.layout.xaxis.Title(
	            text='Date',
	            font=dict(size=18)
	        )
	    ),
	    
	    yaxis=go.layout.YAxis(
	        title=go.layout.yaxis.Title(
	            text='Nbr active ICU patients',
	            font=dict(size=18)
	        )
	    ),
	    
	)


	figure = go.Figure(data=[line],  layout=layout)
	figure.update_layout(
	    xaxis_tickformat='%d %B',
	    #showlegend=True
	)
	# figure.write_html('../../plotly_graph.html')

	return figure

# if __name__ == '__main__':
# 	main()
