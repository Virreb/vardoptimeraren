# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 10:14:44 2020
@author: tilda.lundgren
"""
import pandas as pd
import folium

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
            popup=folium.Popup('<b>'+row.Region+'</b><br><br>From '+str(row.IVA)+' to '+str(row.FinalWithoutOpt)+\
                               ' IVA<br>Organic growth: '+str(row.OrganicGrowth)+\
                               '<br>Allocation: 0'+\
                               '<br>Capacity: '+str(row.Capacity),
                               max_width=450,min_width=150),
            color=color,
            fill=True,
            fill_color=color,
            tooltip="Click here!",
        ).add_to(m)
    
    return m
    
def plot_final_state(mdl,current_df,geojson):
    
    from src.optimization.folium_scripts import get_arrows
    
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
            popup=folium.Popup('<b>'+row.Region+'</b><br><br>From '+str(row.IVA)+' to '+str(row.Final)+\
                               ' IVA<br>Organic growth: '+str(row.OrganicGrowth)+\
                               '<br>Allocation: '+str(row.Allocation)+\
                               '<br>Capacity: '+str(row.Capacity),
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
    
    return m