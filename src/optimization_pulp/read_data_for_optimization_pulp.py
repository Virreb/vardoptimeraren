# -*- coding: utf-8 -*-
"""
Read data for optimization
"""
import pandas as pd
from datetime import date
import folium
 
def read_and_process_data(trend_data, region_data, today = date(2020,4,3)):
    
    # Read forecast
    fc_df = pd.read_csv(trend_data,sep=",")
    fc_df.iva.fillna(fc_df.predicted, inplace=True)
    fc_df = fc_df.drop(columns=['Unnamed: 0',"predicted"])
    fc_df = fc_df.rename(columns={"date": "Date", "iva": "IVA"})
    fc_df.Region = fc_df.Region.apply(lambda x: x.replace("Region ", ""))
    fc_df = fc_df.replace("Örebro län", "Örebro")
    fc_df = fc_df.replace("Jönköpings län", "Jönköping")
    fc_df = fc_df.replace("Kalmar län", "Kalmar")

    # Read region data
    region_df = pd.read_csv(region_data,sep=";")
    region_df.Region = region_df.Region.apply(lambda x: x.replace("Region ", ""))

    # Extract current still image
    current_df = fc_df[fc_df["Date"] == today.strftime("%Y-%m-%d")]

    # Merge current_df with region data
    current_df = current_df.merge(region_df, on=['Region'], how='left')

    # Process current_df
    current_df["UnderCapacity"] = current_df["IVA"] - current_df["Capacity"]
    current_df["UnderCapacity"] = current_df["UnderCapacity"].apply(lambda x: max(0,x))
    current_df["SurplusCapacity"] = current_df["Capacity"] - current_df["IVA"]
    current_df["SurplusCapacity"] = current_df["SurplusCapacity"].apply(lambda x: max(0,x))
    current_df["Rate"] = current_df["IVA"] / current_df["Capacity"]
    current_df = current_df.set_index(current_df.Region)

    # Region data
    trend_dict = {}
    for d in list(region_df.Region):
        data = fc_df[fc_df.Region==d]
        data = data.groupby('Date').sum().reset_index()
        data['Date']=pd.to_datetime(data['Date'])
        data = data.sort_values(by=['Date'], ascending=False)
        trend_dict[d] = data
        
    return current_df, trend_dict

def plot_initial_state(current_df,geojson):
    
    # Initiate map
    m = folium.Map(location=[62, 20], zoom_start=5)
    
    # Define styling rules for counties
    def style_function(feature):
        d = feature['properties']['name']   
        
        if current_df.at[d,"Rate"] < 0.5:
            if current_df.at[d,"SurplusCapacity"] > 3:
                color = 'grey'
            else: 
                color = 'green'
        elif 0.5 <= current_df.at[d,"Rate"] < 0.9:
            color='green'
        elif 0.9 <= current_df.at[d,"Rate"] <= 1:
            color='orange'   
        elif 1 < current_df.at[d,"Rate"]:
            color='red'  
            
        return {'fillOpacity': 0.3,'weight': 0.5,
                'color': 'black','fillColor': color}
    
    # Import geojson data and apply styling rule
    folium.GeoJson(
        geojson,
        name='geojson',
        style_function=style_function
    ).add_to(m)
    
    # Add a clickable circle to each county
    for idx, row in current_df.iterrows():           
        
        # Define styling rules
        if row.Rate < 0.5:
            if row.SurplusCapacity > 3:
                color = 'grey'
            else: 
                color = 'green'
        elif 0.5 <= row.Rate < 0.9:
            color='green'
        elif 0.9 <= row.Rate <= 1:
            color='orange'   
        elif 1 < row.Rate:
            color='red'  
        
        # Draw circle
        folium.Circle(
            radius= 7000 + row.IVA*200,
            location=[row.Lat, row.Long],
            popup=folium.Popup('<b>'+row.Region+'</b><br>'+\
                               '<br>Patienter: '+str(row.IVA)+\
                               '<br>Kapacitet: '+str(row.Capacity),
                               max_width=450,min_width=150),
            color=color,
            fill=True,
            fill_color=color,
            tooltip="Klicka här!",
        ).add_to(m)
    
    return m
