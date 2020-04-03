import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV

import matplotlib.pyplot as plt
from datetime import timedelta
from datetime import datetime

def run_model():		
	data = pd.read_csv('xgboost_input.csv')
	split_date = '2020-03-26'
	train = data[data['date'] < split_date]
	train = train.replace(np.inf, np.nan)
	train = train.dropna()
	test = data[(data['date'] >= split_date) & (data['date'] < '2020-03-31')]
	X = train.drop(['date', 'change_coming_3_days', 'Region', 'cases'], axis=1)
	y = train['change_coming_3_days']

	param_grid = {'n_estimators': [30, 50, 100, 200, 300],
	              'learning_rate': [0.01, 0.03, 0.05, 0.1],
	              'max_depth': [3, 4, 5, 6, 7, 8]
	             }

	model = XGBRegressor(n_estimators=200, learning_rate=0.01, max_depth=4)
	model.fit(X, y)
	X_test = test.drop(['date', 'change_coming_3_days', 'Region', 'cases'], axis=1)
	y_test = test['change_coming_3_days']
	pred = model.predict(X_test)
	test['predicted_change'] = pred
	test['predicted_nbr_in_3_days'] = (test['iva']*test['predicted_change']).astype('int')
	test['iva_in_3_days'] = test['iva']*test['change_coming_3_days']
	test['absolute_error_%'] = abs(test['predicted_change']-test['change_coming_3_days'])/test['change_coming_3_days']
	test['absolute_error_%'].mean()

	return test, model


def results(input_data, output_data):
    results = output_data[['date', 'Region', 'predicted_nbr_in_3_days']]
    results['date'] = [str(datetime.strptime(day, '%Y-%m-%d').date()+timedelta(days=3)) for day in results['date']]
    results.columns = ['date', 'Region', 'predicted']

    results = results.merge(input_data, on=['date', 'Region'], how='left')[['date', 'Region', 'predicted', 'iva']]
    results['absolute_error_%'] = abs(results['predicted']-results['iva'])/results['iva']
    
    return results