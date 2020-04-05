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
                color = '#7AA826' #green
            else: 
                color = '#FFCA2D' #yellow
        elif 0.5 <= current_df.at[d,"Rate"] < 0.9:
            color='#FFCA2D' #yellow
        elif 0.9 <= current_df.at[d,"Rate"] <= 1:
            color='#EA830E' #orange 
        elif 1 < current_df.at[d,"Rate"]:
            color='#BF2C2A'  #red
            
        return {'fillOpacity': 0.4,'weight': 0.5,
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
                color = '#7AA826' #green
            else: 
                color = '#FFCA2D' #yellow
        elif 0.5 <= row.Rate < 0.9:
            color='#FFCA2D' #yellow
        elif 0.9 <= row.Rate <= 1:
            color='#EA830E' #orange
        elif 1 < row.Rate:
            color='#BF2C2A'  #red
        
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
        
    from branca.element import Template, MacroElement

    template = """
    {% macro html(this, kwargs) %}

    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>jQuery UI Draggable - Default functionality</title>
      <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

      <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

      <script>
      $( function() {
        $( "#maplegend" ).draggable({
                        start: function (event, ui) {
                            $(this).css({
                                right: "auto",
                                top: "auto",
                                bottom: "auto"
                            });
                        }
                    });
    });

      </script>
    </head>
    <body>


    <div id='maplegend' class='maplegend' 
        style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
         border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>

    <div class='legend-title'>Color code explanation</div>
    <div class='legend-scale'>
      <ul class='legend-labels'>
        <li><span style='background:#BF2C2A;opacity:0.7;'></span>Over 100% of capacity</li>
        <li><span style='background:#EA830E;opacity:0.7;'></span>Between 90% and 100% of capacity</li>
        <li><span style='background:#FFCA2D;opacity:0.7;'></span>Between 50% and 90% of capacity</li>
        <li><span style='background:#7AA826;opacity:0.7;'></span>Less than 50% of capacity</li>

      </ul>
    </div>
    </div>

    </body>
    </html>

    <style type='text/css'>
      .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
        }
      .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
        }
      .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
        }
      .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #999;
        }
      .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
        }
      .maplegend a {
        color: #777;
        }
    </style>
    {% endmacro %}"""

    macro = MacroElement()
    macro._template = Template(template)
    m.get_root().add_child(macro)
    
    return m
