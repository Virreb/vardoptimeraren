# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 08:32:01 2020
@author: tilda.lundgren
"""

import pulp as plp
import pickle

def check_environment():
    from docplex.mp.environment import Environment
    env = Environment()
    
    if not env.has_cplex: 
        print("CPLEX not installed.")
    else:
        print("CPLEX is installed.\n")
        env.print_information()
        
def build_model():
    mdl = plp.LpProblem("PatientAllocation")
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
    mdl.x_vars = {(d1,d2,p): plp.LpVariable(cat=plp.LpBinary,name="x_{0}_{1}_{2}".format(d1,d2,p)) 
                  for d1 in mdl.deps for d2 in mdl.deps for p in mdl.transfer_periods}
    
    # y_d1_d2 = nb if nb patients are sent on link between department 1 and 2
    mdl.y_vars = {(d1,d2,p): plp.LpVariable(cat=plp.LpInteger,name="y_{0}_{1}_{2}".format(d1,d2,p),
                                           upBound = mdl.MAX_CASES_PER_LONG_TRANSFERS, lowBound = 0)
                  for d1 in mdl.deps for d2 in mdl.deps for p in mdl.transfer_periods}
    
    # o_d_p = nb if nb patients are placed at department d at period p
    mdl.o_vars = {(d,p): plp.LpVariable(cat=plp.LpInteger,name="o_{0}_{1}".format(d,p), lowBound = 0) 
                  for d in mdl.deps for p in mdl.all_periods}
    
    # Maximum undercapacity among departments
    mdl.max_under = plp.LpVariable(cat=plp.LpContinuous, lowBound=0, name = "max_under")
    
    # Maximum overcapacity among departments
    mdl.max_over = plp.LpVariable(cat=plp.LpContinuous, lowBound=0, name = "max_over")
    
    return mdl

def calculate_distances(mdl, current_df, path_to_static_distances):
    
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
    
    #mdl.dep_distances = {d1:{d2:distance(current_df[current_df.Region == d1].Lat.values[0], 
    #                                     current_df[current_df.Region == d1].Long.values[0], 
    #                                     current_df[current_df.Region == d2].Lat.values[0], 
    #                                     current_df[current_df.Region == d2].Long.values[0])
    #                    for d2 in mdl.deps} 
    #                    for d1 in mdl.deps}
        
    with open(path_to_static_distances, 'rb') as handle:
        mdl.dep_distances = pickle.load(handle)
    
    mdl.is_long = {d1:{d2: mdl.dep_distances[d1][d2] > mdl.THRESHOLD_FOR_LONG_DISTANCE
                  for d2 in mdl.deps} 
                  for d1 in mdl.deps}
    
    return mdl