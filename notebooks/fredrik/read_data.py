import pandas as pd
from datetime import datetime


def read_and_merge_sources():
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


