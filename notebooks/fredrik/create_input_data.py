# Create dataframe with all regions
import pandas as pd

import functions_dataprep
import read_data

def create_input_data():
	df = read_data.read_and_merge_sources()
	cases = read_data.read_case_data()
	regions = list(df['Region'].unique())

	for i, region in enumerate(regions):
	    if i == 0:
	        data = functions_dataprep.create_dataframe_per_region(df, region, cases)
	        
	    else:
	        tmp_data = functions_dataprep.create_dataframe_per_region(df, region, cases)
	        data = pd.concat([data, tmp_data])
	        
	data['iva_per_1000'] = data['iva']/data['befolkning']*1000

	return data


def main():
	create_input_data().to_csv('xgboost_input.csv', index=False)

if __name__ == "__main__":
	main()