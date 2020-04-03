import pandas as pd

region_keys = {'Region Stockholm': 'Stockholm','Region Sörmland': 'Sörmland',  
                 'Region Östergötland': 'Östergötland', 'Region Jönköpings län': 'Jönköping',
                 'Region Kronoberg': 'Kronoberg','Region Kalmar län': 'Kalmar',
                 'Region Blekinge': 'Blekinge', 'Region Skåne': 'Skåne',
                 'Region Halland': 'Halland', 'Västra Götalandsregionen': 'Västra_Götaland',
                 'Region Värmland': 'Värmland', 'Region Örebro län': 'Örebro', 
                 'Region Västmanland': 'Västmanland', 'Region Dalarna': 'Dalarna',
                 'Region Gävleborg': 'Gävleborg', 'Region Västernorrland': 'Västernorrland',
                 'Region Jämtland Härjedalen': 'Jämtland_Härjedalen', 'Region Västerbotten': 'Västerbotten',
                 'Region Norrbotten': 'Norrbotten', 'Region Uppsala': 'Uppsala'
                }

def get_cases_per_day_and_region(cases, region):
    # Change key name
    region = region_keys[region]
    
    tmp_df = cases[cases['Region'] == region]
    dates = pd.date_range('2020-03-06', '2020-03-31')
    dates = [str(date.date()) for date in dates]
    values = [tmp_df[date].iloc[0] for date in dates]
    values = [sum(values[:i]) for i in range(len(values))]
    tmp_df = pd.DataFrame({'date': dates, 'cases': values})
    tmp_df['Region'] = region
    return tmp_df


def create_dataframe_per_region(df, region, cases):
    tmp_df = df[df['Region'] == region]
    #tmp_df.drop(['2020-04-01', '2020-03-31', '2020-03-30', '2020-03-29'], axis=1, inplace=True)
    dates = tmp_df.drop(['Region', 'Befolkning', 'Medelålder'], axis=1).columns
    values = tmp_df.drop(['Region', 'Befolkning', 'Medelålder'], axis=1).iloc[0].values
    befolkning = tmp_df['Befolkning'].values[0]
    mean_age = tmp_df['Medelålder'].values[0]
    tmp_df = pd.DataFrame({'date': dates, 'iva': values})
    tmp_df['befolkning'] = befolkning 
    tmp_df['mean_age'] =  mean_age
    tmp_df['Region'] = region
    tmp_df = add_change_coming_x_days(tmp_df, 3)
    for i in range(1, 8):
        tmp_df = add_change_since_x_days_ago(tmp_df, i)
    #for i in range(1, 8):
     #   tmp_df = add_change_in_nbrs_since_x_days_ago(tmp_df, i)
        
    # Add data about cases
    cases_df = get_cases_per_day_and_region(cases, region)
    tmp_df = tmp_df.merge(cases_df.drop('Region', axis=1), on='date', how='left')
    #for i in range(7, 14):
     #   tmp_df = add_change_in_cases_since_x_days_ago(tmp_df, i)
    tmp_df = add_case_change_from_day_10_to_4(tmp_df)
    return tmp_df


def add_change_since_x_days_ago(df, x):
    change = []
    for i in range(len(df)):
        if i < x:
            change.append(None)
        else:
            change.append(df['iva'].iloc[i]/df['iva'].iloc[i-x])
    df['change_since_'+str(x)+'_days'] = change
    return df


def add_growth_factor_x_days_ago(df, x):
    change = []
    for i in range(len(df)):
        if i < x:
            change.append(None)
        else:
            change.append(df['iva'].iloc[i-x+1]/df['iva'].iloc[i-x])
    df['growth_'+str(x)+'_days_ago'] = change
    return df


def add_change_coming_x_days(df, x):
    change = []
    for i in range(len(df)):
        if len(df) - i - 1 < x:
            change.append(None)
        else:
            change.append(df['iva'].iloc[i+x]/df['iva'].iloc[i])
    df['change_coming_'+str(x)+'_days'] = change
    return df


def add_change_in_nbrs_since_x_days_ago(df, x):
    change = []
    for i in range(len(df)):
        if i < x:
            change.append(None)
        else:
            change.append(df['iva'].iloc[i] - df['iva'].iloc[i-x])
    df['change_in_nbrs_since_'+str(x)+'_days'] = change
    return df


def add_change_in_cases_since_x_days_ago(df, x):
    change = []
    for i in range(len(df)):
        if i < x:
            change.append(None)
        else:
            change.append(df['cases'].iloc[i]/df['cases'].iloc[i-x])
    df['cases_change_since_'+str(x)+'_days'] = change
    return df


def add_case_change_from_day_10_to_4(df):
    change = []
    for i in range(len(df)):
        if i < 10:
            change.append(None)
        else:
            change.append(df['cases'].iloc[i-4]/df['cases'].iloc[i-10])
    df['case_change_from_day_10_to_4'] = change
    return df


def add_case_growth_factor_x_days_ago(df, x):
    change = []
    for i in range(len(df)):
        if i < x:
            change.append(None)
        else:
            change.append(df['cases'].iloc[i-x+1]/df['cases'].iloc[i-x])
    df['case_growth_'+str(x)+'_days_ago'] = change
    return df