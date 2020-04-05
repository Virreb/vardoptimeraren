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
    
    mdl.over_cap_abs_max = plp.LpVariable(cat=plp.LpContinuous, lowBound=-100000, name = "under_cap_abs_max")
    mdl.over_cap_rel_max = plp.LpVariable(cat=plp.LpContinuous, lowBound=-100000, name = "under_cap_rel_max")

    for d in mdl.deps:
        over_cap_abs = mdl.o_vars[d, mdl.NB_PERIODS] - current_df.at[d,"Capacity"] 
        mdl.addConstraint(plp.LpConstraint(e=mdl.over_cap_abs_max - over_cap_abs,
                                           sense=plp.LpConstraintGE,
                                           rhs=0,
                                           name="max_over_cap_abs_{0}".format(d)))

    for d in mdl.deps:
        over_cap_rel = (mdl.o_vars[d, mdl.NB_PERIODS] - current_df.at[d,"Capacity"])/current_df.at[d,"Capacity"]
        mdl.addConstraint(plp.LpConstraint(e=mdl.over_cap_rel_max - over_cap_rel,
                                           sense=plp.LpConstraintGE,
                                           rhs=0,
                                           name="max_over_cap_rel_{0}".format(d)))
    return mdl

def define_distance_measures(mdl):
    # ----------------------------------------------------------------------- #
    # Minimize patient transfers
    # ----------------------------------------------------------------------- #   
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
                         w_overcap_abs = 1,
                         w_overcap_rel = 1,
                         w_nb_trans = 1,
                         w_km_trans = 1):
    
    # ----------------------------------------------------------------------- #
    # Summarize all
    # ----------------------------------------------------------------------- #  
    mdl.sense = plp.LpMinimize
    mdl.setObjective(w_overcap_abs  * 1 * mdl.over_cap_abs_max +\
                     w_overcap_rel  * 10  * mdl.over_cap_rel_max +\
                     w_nb_trans     * 0.01 * mdl.nb_patient_transfers + \
                     w_km_trans     * 0.001 * mdl.km_patient_transfers )
    return mdl