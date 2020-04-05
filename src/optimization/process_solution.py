# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 10:14:44 2020
@author: tilda.lundgren
"""
import pandas as pd
import folium
from collections import namedtuple
import numpy as np

def get_arrows(locations, color='black', size=6, n_arrows=3): 
    '''
    Get a list of correctly placed and rotated 
    arrows/markers to be plotted
    Parameters
    locations : list of lists of lat lons that represent the 
                start and end of the line. 
                eg [[41.1132, -96.1993],[41.3810, -95.8021]]
    arrow_color : default is 'blue'
    size : default is 6
    n_arrows : number of arrows to create.  default is 3    Return
    list of arrows/markers
    '''
    
    Point = namedtuple('Point', field_names=['lat', 'lon'])
    
    # creating point from our Point named tuple
    p1 = Point(locations[0][0], locations[0][1])
    p2 = Point(locations[1][0], locations[1][1])
    
    # getting the rotation needed for our marker.  
    rotation = get_bearing(p1, p2) - 90
    
    # get an evenly space list of lats and lons for our arrows
    arrow_lats = np.linspace(p1.lat, p2.lat, n_arrows + 2)[1:n_arrows+1]
    arrow_lons = np.linspace(p1.lon, p2.lon, n_arrows + 2)[1:n_arrows+1]  
    
    #creating each "arrow" and appending them to our arrows list
    arrows = []
    for points in zip(arrow_lats, arrow_lons):
        arrows.append(folium.RegularPolygonMarker(location=points, 
                      fill_color=color, color=color, number_of_sides=3, 
                      radius=size, rotation=rotation))
    return arrows

def get_bearing(p1, p2):   
    '''
    Returns compass bearing from p1 to p2
    Parameters
    p1 : namedtuple with lat lon
    p2 : namedtuple with lat lon
    Return
    compass bearing of type float
    Notes
    Based on https://gist.github.com/jeromer/2005586
    '''
    
    long_diff = np.radians(p2.lon - p1.lon)
    lat1 = np.radians(p1.lat)
    lat2 = np.radians(p2.lat)
    
    x = np.sin(long_diff) * np.cos(lat2)
    y = (np.cos(lat1) * np.sin(lat2) 
        - (np.sin(lat1) * np.cos(lat2) 
        * np.cos(long_diff)))    
    bearing = np.degrees(np.arctan2(x, y))
    if bearing < 0:
        return bearing + 360
    return bearing

def process_allocations(mdl):
    
    mdl.edges = [(t, d1, d2, int(mdl.y_vars[d1, d2, t]), mdl.is_long[d1][d2]) 
         for t in mdl.transfer_periods 
         for d1 in mdl.deps 
         for d2 in mdl.deps 
         if int(mdl.y_vars[d1, d2, t]) >= 1]

    mdl.allocation_plan = pd.DataFrame(columns=["Från","Till","Antal"])
    for edge in mdl.edges: 
        temp = {'Från' : edge[1] , 'Till' : edge[2], 'Antal': edge[3]}
        mdl.allocation_plan = mdl.allocation_plan.append(temp, ignore_index = True)
        
    return mdl

def process_final_data(mdl,current_df,trend_dict,today,target_day):
    
    final = {d: int(mdl.o_vars[d, mdl.NB_PERIODS].solution_value) for d in mdl.deps}

    organic = {}
    for d in mdl.deps:    
        prognosis = trend_dict[d][trend_dict[d]["Date"] == target_day].IVA.values[0]
        current = trend_dict[d][trend_dict[d]["Date"] == today].IVA.values[0]
        organic_growth = prognosis - current
        organic[d] = organic_growth
            
    current_df["Final"] = [final[d] for d in mdl.deps]
    current_df["OrganicGrowth"] = [organic[d] for d in mdl.deps]
    current_df["FinalUnderCapacity"] = current_df["Final"] - current_df["Capacity"]
    current_df["FinalUnderCapacity"] = current_df["FinalUnderCapacity"].apply(lambda x: max(0,x))
    current_df["FinalSurplusCapacity"] = current_df["Capacity"] - current_df["Final"]
    current_df["FinalSurplusCapacity"] = current_df["FinalSurplusCapacity"].apply(lambda x: max(0,x))
    current_df["Allocation"] = current_df["Final"] - current_df["IVA"] - current_df["OrganicGrowth"] 
    current_df["RateFinal"] = current_df["Final"]/current_df["Capacity"]
    current_df["FinalWithoutOpt"] = current_df["IVA"] + current_df["OrganicGrowth"]
    current_df["FinalWithoutOptRate"] = current_df["FinalWithoutOpt"] / current_df["Capacity"]
    current_df["FinalSurplusCapacityWithoutOpt"] = current_df["Capacity"] - current_df["FinalWithoutOpt"]
    current_df["FinalSurplusCapacityWithoutOpt"] = current_df["FinalSurplusCapacityWithoutOpt"].apply(lambda x: max(0,x))
    
    return mdl, current_df

def plot_final_state_without_opt(mdl,current_df,geojson):
    
    # Initiate map
    m = folium.Map(location=[62, 20], zoom_start=5)
    
    # Define styling rules for counties
    def style_function(feature):
        d = feature['properties']['name']    
    
        if current_df.at[d,"FinalWithoutOptRate"] < 0.5:
            if current_df.at[d,"FinalSurplusCapacityWithoutOpt"] > 3:
                color = '#7AA826' #green
            else: 
                color = '#FFCA2D' #yellow
        elif 0.5 <= current_df.at[d,"FinalWithoutOptRate"] < 0.9:
            color='#FFCA2D' #yellow
        elif 0.9 <= current_df.at[d,"FinalWithoutOptRate"] <= 1:
            color='#EA830E' #orange   
        elif 1 < current_df.at[d,"FinalWithoutOptRate"]:
            color='#BF2C2A'  #red 
    
        return {'fillOpacity': 0.4,'weight': 0.5,
                'color': 'black','fillColor': color}
    
    # Import geojson data and apply styling rule
    geo = folium.GeoJson(
        geojson,
        name='geojson',
        style_function=style_function
    ).add_to(m)
    
    # Add a clickable circle to each county
    for idx, row in current_df.iterrows():    
    
        # Define styling rules
        if row.FinalWithoutOptRate < 0.5:
            if row.FinalSurplusCapacityWithoutOpt > 3:
                color = '#7AA826' #green
            else: 
                color = '#FFCA2D' #yellow
        elif 0.5 <= row.FinalWithoutOptRate < 0.9:
            color='#FFCA2D' #yellow
        elif 0.9 <= row.FinalWithoutOptRate <= 1:
            color='#EA830E' #orange    
        elif 1 < row.FinalWithoutOptRate:
            color='#BF2C2A'  #red  
    
        # Draw circle
        folium.Circle(
            radius= 7000 + row.Final*200,
            location=[row.Lat, row.Long],
            popup=folium.Popup('<b>'+row.Region+'</b><br><br>From '+str(int(row.IVA))+' to '+str(int(row.FinalWithoutOpt))+\
                               ' IVA<br>Organic growth: '+str(int(row.OrganicGrowth))+\
                               '<br>Allocation: 0'+\
                               '<br>Capacity: '+str(int(row.Capacity)),
                               max_width=450,min_width=150),
            color=color,
            fill=True,
            fill_color=color,
            tooltip="Click here!",
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
    
def plot_final_state(mdl,current_df,geojson):
        
    # Initiate map
    m = folium.Map(location=[62, 20], zoom_start=5)
    
    # Define styling rules for counties
    def style_function(feature):
        d = feature['properties']['name']    
        
        if current_df.at[d,"RateFinal"] < 0.5:
            if current_df.at[d,"FinalSurplusCapacity"] > 3:
                color = '#7AA826' #green
            else: 
                color = '#FFCA2D' #yellow
        elif 0.5 <= current_df.at[d,"RateFinal"] < 0.9:
            color='#FFCA2D' #yellow
        elif 0.9 <= current_df.at[d,"RateFinal"] <= 1:
            color='#EA830E' #orange   
        elif 1 < current_df.at[d,"RateFinal"]:
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
        if row.RateFinal < 0.5:
            if row.FinalSurplusCapacity > 3:
                color = '#7AA826' #green
            else: 
                color = '#FFCA2D' #yellow
        elif 0.5 <= row.RateFinal < 0.9:
            color='#FFCA2D' #yellow
        elif 0.9 <= row.RateFinal <= 1:
            color='#EA830E' #orange    
        elif 1 < row.RateFinal:
            color='#BF2C2A'  #red  
            
        # Draw circle
        folium.Circle(
            radius= 7000 + row.Final*200,
            location=[row.Lat, row.Long],
            popup=folium.Popup('<b>'+row.Region+'</b><br><br>From '+str(int(row.IVA))+' to '+str(int(row.Final))+\
                               ' IVA<br>Organic growth: '+str(int(row.OrganicGrowth))+\
                               '<br>Allocation: '+str(int(row.Allocation))+\
                               '<br>Capacity: '+str(int(row.Capacity)),
                               max_width=450,min_width=150),
            color=color,
            fill=True,
            fill_color=color,
            tooltip="Click here!",
        ).add_to(m)
      
    # Add arrows and lines
    for (period, d1, d2, nb, il) in mdl.edges: 
        
        # Find arrow coordinates
        coordinates = [[current_df.at[d1,"Lat"], current_df.at[d1,"Long"]], 
                       [current_df.at[d2,"Lat"], current_df.at[d2,"Long"]]]
        
        # Define tooltop
        if nb == 1:
            tooltip = str(nb)+" patient from "+d1+" to "+d2
        elif nb > 1:
            tooltip = str(nb)+" patients from "+d1+" to "+d2
        
        # Draw line
        pl = folium.PolyLine(coordinates, color="black", weight=3,tooltip=tooltip)
        m.add_child(pl)    
        
        # Draw arrows
        arrows = get_arrows(locations=coordinates, color="black", size=3, n_arrows=1)
        for arrow in arrows:
            arrow.add_to(m)
    
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