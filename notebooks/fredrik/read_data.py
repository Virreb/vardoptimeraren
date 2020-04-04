import pandas as pd
from datetime import datetime
import os


def update_iva_data_if_possible():
        if os.path.exists('../../data/interim/iva_kumulativ.xlsx'):
                iva_data = pd.read_excel('../../data/interim/iva_kumulativ.xlsx')
                last_date = iva_data.columns[-1]
                for filename in os.listdir('../../data/raw/iva_data/'):
                        date = filename.split(' - ')[2].split('.')[0]
                        if date > last_date:
                                iva_data = create_new_iva_data()
                                break
        else:
                iva_data = create_new_iva_data()

        iva_data.to_excel('../../data/interim/iva_kumulativ.xlsx')


def create_new_iva_data():
        for i, filename in enumerate(os.listdir('../../data/raw/iva_data/')):
            print(filename)
            data = pd.read_excel('../../data/raw/iva_data/'+filename, skiprows=1)
            data.columns = ['Region', 'Cases', 'Persons']
            if i==0:
                regioner = list(data['Region'].unique())
                nbr_cases = data['Persons'].values
                date = filename.split(' - ')[2].split('.')[0]
                iva_data = pd.DataFrame({'Region': data['Region'], date: nbr_cases})
            else:
                nbr_cases = data['Persons'].values
                date = filename.split(' - ')[2].split('.')[0]
                tmp_df = pd.DataFrame({'Region': data['Region'], str(date): nbr_cases})
                iva_data = iva_data.merge(tmp_df, on='Region', how='outer')
            
        iva_data = iva_data.set_index('Region')
        iva_data = iva_data.reindex(sorted(iva_data.columns), axis=1)
        return iva_data
        


def read_and_merge_sources():
        update_iva_data_if_possible()
        df = pd.read_excel('../../data/interim/iva_kumulativ.xlsx')
        df = df[df['Region'] != 'Hela riket']
        befolkning = pd.read_excel('../../data/raw/befolkning.xlsx', skiprows=9)
        befolkning = befolkning[['Hela riket', 10327589, 41.313715]]
        befolkning.dropna(inplace=True)
        befolkning.columns = ['Region', 'Befolkning', 'Medelålder']
        befolkning.reset_index(inplace=True)
        befolkning.drop('index', axis=1, inplace=True)

        lan_to_region = {'Stockholms län': 'Region Stockholm', 'Södermanlands län': 'Region Sörmland', 
                         'Östergötlands län': 'Region Östergötland', 'Jönköpings län': 'Region Jönköpings län',
                         'Kronobergs län': 'Region Kronoberg', 'Kalmar län': 'Region Kalmar län',
                         'Blekinge län': 'Region Blekinge', 'Skåne län': 'Region Skåne',
                         'Hallands län': 'Region Halland', 'Västra Götalands län': 'Västra Götalandsregionen',
                         'Värmlands län': 'Region Värmland', 'Örebro län': 'Region Örebro län', 
                         'Västmanlands län': 'Region Västmanland', 'Dalarnas län': 'Region Dalarna',
                         'Gävleborgs län': 'Region Gävleborg', 'Västernorrlands län': 'Region Västernorrland',
                         'Jämtlands län': 'Region Jämtland Härjedalen', 'Västerbottens län': 'Region Västerbotten',
                         'Norrbottens län': 'Region Norrbotten', 'Uppsala län': 'Region Uppsala', 
                         'Gotlands län': 'Region Gotland'
                        }

        befolkning['Region'] = [lan_to_region[val] for val in befolkning['Region']]
        df = df.merge(befolkning, on='Region', how='inner')

        return df


def read_case_data():
        cases = pd.read_csv('../../data/folkhalsomyndigheten_covid19.csv')
        cases.columns = [str(datetime.strptime(col, '%Y-%m-%d %H:%M:%S').date()) if col != 'Region' else col
                         for col in cases.columns
                        ]
        return cases     


