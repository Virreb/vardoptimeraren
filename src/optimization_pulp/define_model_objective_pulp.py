# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 09:58:09 2020
@author: tilda.lundgren
"""
import pulp as plp

def define_max_overcapacity(mdl,current_df):
    # ----------------------------------------------------------------------- #
    # Max overcapacity
    # ----------------------------------------------------------------------- #  
    
    mdl.over_cap_max = plp.LpVariable(cat=plp.LpContinuous, lowBound=-100000, name = "over_cap_max")

    for d in mdl.deps:

        over_capacity = mdl.o_vars[d, mdl.NB_PERIODS] - current_df.at[d,"Capacity"]
        mdl.addConstraint(plp.LpConstraint(e=mdl.over_cap_max - over_capacity,
                                           sense=plp.LpConstraintGE,
                                           rhs=0,
                                           name="max_overcapacity_{0}".format(d)))
    return mdl

def define_distance_measures(mdl):
    # ----------------------------------------------------------------------- #
    # Minimize patient transfers
    # ----------------------------------------------------------------------- #   
    mdl.nb_long_transfers = plp.lpSum(mdl.x_vars[d1, d2, t] 
                                for d1 in mdl.deps 
                                for d2 in mdl.deps 
                                if mdl.is_long[d1][d2] 
                                for t in mdl.transfer_periods)
    
    mdl.nb_short_transfers = plp.lpSum(mdl.x_vars[d1, d2, t] 
                                 for d1 in mdl.deps 
                                 for d2 in mdl.deps 
                                 if not mdl.is_long[d1][d2] 
                                 for t in mdl.transfer_periods)
    
    mdl.nb_patient_transfers = plp.lpSum(mdl.y_vars[d1, d2, t] 
                                 for d1 in mdl.deps 
                                 for d2 in mdl.deps
                                 for t in mdl.transfer_periods)
    
    mdl.km_patient_transfers = plp.lpSum(mdl.y_vars[d1, d2, t] * mdl.dep_distances[d1][d2]
                                 for d1 in mdl.deps 
                                 for d2 in mdl.deps
                                 for t in mdl.transfer_periods)
    return mdl

def summarize_objectives(mdl,
                         w_total_undercapacity = 100,
                         w_max_under = 0,
                         w_max_over = 0,
                         w_nb_patient_transfers = 1,
                         w_km_patient_transfers = 0.01,
                         w_nb_long_transfers = 0.01):
    
    # ----------------------------------------------------------------------- #
    # Summarize all
    # ----------------------------------------------------------------------- #  
    mdl.sense = plp.LpMinimize
    mdl.setObjective(w_total_undercapacity   * mdl.over_cap_max +\
                     w_nb_patient_transfers  * mdl.nb_patient_transfers + \
                     w_km_patient_transfers  * mdl.km_patient_transfers + \
                     w_nb_long_transfers     * mdl.nb_long_transfers)
    return mdl