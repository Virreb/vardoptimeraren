# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 09:58:09 2020
@author: tilda.lundgren
"""

def define_max_overcapacity(mdl,current_df):
    # ----------------------------------------------------------------------- #
    # Max overcapacity
    # ----------------------------------------------------------------------- #  
    
    mdl.under_cap_abs_max = mdl.continuous_var(lb=-100000,  name = "under_cap_abs_max")
    mdl.under_cap_rel_max = mdl.continuous_var(lb=-100000, name = "under_cap_rel_max")
    mdl.over_cap_rel_max = mdl.continuous_var(lb=-100000, name = "over_cap_rel_max")
    mdl.over_cap_abs_max = mdl.continuous_var(lb=-100000, name = "over_cap_abs_max")
    
    for d in mdl.deps:
        under_cap_abs = mdl.o_vars[d, mdl.NB_PERIODS] - current_df.at[d,"Capacity"]
        mdl.add_constraint(ct = mdl.under_cap_abs_max - under_cap_abs >= 0, 
                           ctname = "max_under_cap_abs_{0}".format(d))
        
        over_cap_abs = current_df.at[d,"Capacity"]-mdl.o_vars[d, mdl.NB_PERIODS]
        mdl.add_constraint(ct = mdl.over_cap_abs_max - over_cap_abs >= 0, 
                           ctname = "max_over_cap_rel_{0}".format(d))

    for d in mdl.deps:
        under_cap_rel = (mdl.o_vars[d, mdl.NB_PERIODS] - current_df.at[d,"Capacity"])/current_df.at[d,"Capacity"]
        mdl.add_constraint(ct = mdl.under_cap_rel_max - under_cap_rel >= 0, 
                           ctname = "max_under_cap_rel_{0}".format(d))
        
        over_cap_rel = (current_df.at[d,"Capacity"]-mdl.o_vars[d, mdl.NB_PERIODS])/current_df.at[d,"Capacity"]
        mdl.add_constraint(ct = mdl.over_cap_rel_max - over_cap_rel >= 0, 
                           ctname = "max_over_cap_rel_{0}".format(d))
        
    return mdl

def define_distance_measures(mdl):
    # ----------------------------------------------------------------------- #
    # Minimize patient transfers
    # ----------------------------------------------------------------------- #   
    
    mdl.nb_patient_transfers = mdl.sum(mdl.y_vars[d1, d2, t] 
                                 for d1 in mdl.deps 
                                 for d2 in mdl.deps
                                 for t in mdl.transfer_periods)
    
    mdl.km_patient_transfers = mdl.sum(mdl.y_vars[d1, d2, t] * mdl.dep_distances[d1][d2]
                                 for d1 in mdl.deps 
                                 for d2 in mdl.deps
                                 for t in mdl.transfer_periods)
    return mdl

def summarize_objectives(mdl,
                         w_undercap = 1,
                         w_overcap = 1, 
                         w_nb_trans = 1, 
                         w_km_trans = 1):
    
    # ----------------------------------------------------------------------- #
    # Summarize all
    # ----------------------------------------------------------------------- #   
    mdl.minimize(w_undercap     * 1     * mdl.under_cap_abs_max +\
                 w_undercap     * 10    * mdl.under_cap_rel_max +\
                 w_overcap      * 0.1   * mdl.over_cap_abs_max +\
                 w_overcap      * 0.1   * mdl.over_cap_rel_max +\
                 w_nb_trans     * 0.01  * mdl.nb_patient_transfers + \
                 w_km_trans     * 0.001 * mdl.km_patient_transfers )
    return mdl