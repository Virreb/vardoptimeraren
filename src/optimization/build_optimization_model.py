# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 08:32:01 2020
@author: tilda.lundgren
"""

def check_environment():
    from docplex.mp.environment import Environment
    env = Environment()
    
    if not env.has_cplex: 
        print("CPLEX not installed.")
    else:
        print("CPLEX is installed.\n")
        env.print_information()
   
def build_model():
    from docplex.mp.model import Model
    mdl = Model("PatientAllocations")
    return mdl
    
def define_model_parameters_and_sets(mdl,current_df):
    
    # Define parameters
    mdl.NB_PERIODS = 1
    mdl.MAX_NB_LONG_TRANSFERS_PER_PERIOD = 100
    mdl.MAX_CASES_PER_LONG_TRANSFERS = 50
    mdl.MAX_CASES_PER_SHORT_TRANSFERS = 50
    mdl.MAX_NB_SHORT_TRANSFERS_PER_DEPARTMENT = 100
    mdl.THRESHOLD_FOR_LONG_DISTANCE = 200
    mdl.EXEMPT = ["Gotland","Jämtland Härjedalen"]
    
    # Sets
    mdl.deps = list(current_df.Region)
    mdl.transfer_periods = list(range(mdl.NB_PERIODS))
    mdl.all_periods = list(range(mdl.NB_PERIODS+1))
    
    return mdl

def define_model_variables(mdl):
    
    # x_d1_d2 = 1 if link between department 1 and 2 is used
    mdl.x_vars = {(d1,d2,p): mdl.binary_var(name="x_{0}_{1}_{2}".format(d1,d2,p)) 
              for d1 in mdl.deps for d2 in mdl.deps for p in mdl.transfer_periods}
    
    # y_d1_d2 = nb if nb patients are sent on link between department 1 and 2
    mdl.y_vars = {(d1,d2,p): mdl.integer_var(name="y_{0}_{1}_{2}".format(d1,d2,p),
                   ub = mdl.MAX_CASES_PER_LONG_TRANSFERS) 
                   for d1 in mdl.deps for d2 in mdl.deps for p in mdl.transfer_periods}
    
    # o_d_p = nb if nb patients are placed at department d at period p
    mdl.o_vars = {(d,p): mdl.integer_var(name="o_{0}_{1}".format(d,p), lb = 0) 
                  for d in mdl.deps for p in mdl.all_periods}
    
    # Maximum undercapacity among departments
    mdl.max_under = mdl.continuous_var(lb=0, name = "max_under")
    
    # Maximum overcapacity among departments
    mdl.max_over = mdl.continuous_var(lb=0, name = "max_over")
    
    return mdl

def calculate_distances(mdl, current_df):
    
    def distance(lt1, lg1, lt2, lg2):
        import math
        R = 6373.0
        lat1 = math.radians(lt1); lon1 = math.radians(lg1);
        lat2 = math.radians(lt2); lon2 = math.radians(lg2);
        dlon = lon2 - lon1; dlat = lat2 - lat1;
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance
    
    mdl.dep_distances = {d1:{d2:distance(current_df[current_df.Region == d1].Lat.values[0], 
                                         current_df[current_df.Region == d1].Long.values[0], 
                                         current_df[current_df.Region == d2].Lat.values[0], 
                                         current_df[current_df.Region == d2].Long.values[0])
                        for d2 in mdl.deps} 
                        for d1 in mdl.deps}
    
    mdl.is_long = {d1:{d2:distance(current_df[current_df.Region == d1].Lat.values[0], 
                                   current_df[current_df.Region == d1].Long.values[0], 
                                   current_df[current_df.Region == d2].Lat.values[0], 
                                   current_df[current_df.Region == d2].Long.values[0]) > mdl.THRESHOLD_FOR_LONG_DISTANCE
                        for d2 in mdl.deps} 
                        for d1 in mdl.deps}
    
    mdl.dep_neighbor = {}
    for dep in mdl.deps: 
        dx = mdl.dep_distances[dep]
        ordered = {k: v for k, v in sorted(dx.items(), key=lambda item: item[1])}
        neighbors = list(ordered.keys())[1:4]
        mdl.dep_neighbor[dep] = neighbors
    
    return mdl