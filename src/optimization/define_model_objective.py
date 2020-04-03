# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 09:58:09 2020
@author: tilda.lundgren
"""

def define_total_undercapacity(mdl,current_df):
    # ----------------------------------------------------------------------- #
    # Total undercapacity
    # ----------------------------------------------------------------------- #  
    mdl.total_undercapacity = mdl.sum(mdl.max(0,mdl.o_vars[d, mdl.NB_PERIODS] - current_df.at[d,"Capacity"] ) 
                                  for d in mdl.deps)
    return mdl

def undercapacity_distribution(mdl,current_df):
    # ----------------------------------------------------------------------- #
    # Even distribution of undercapacity
    # ----------------------------------------------------------------------- #   
    for d in mdl.deps:
        undercapacity = mdl.max(0,mdl.o_vars[d, mdl.NB_PERIODS] - current_df.at[d,"Capacity"] )
        mdl.add_constraint(ct = mdl.max_under >= undercapacity,
                           ctname = "max_undercapacity_{0}".format(d))
    return mdl

def overcapacity_distribution(mdl, current_df):
    # ----------------------------------------------------------------------- #
    # Even distribution of overcapacity
    # ----------------------------------------------------------------------- #   
    for d in mdl.deps:
        overcapacity = mdl.max(0, current_df.at[d,"Capacity"] - mdl.o_vars[d, mdl.NB_PERIODS])
        mdl.add_constraint(ct = mdl.max_over >= overcapacity,
                           ctname = "max_relative_overcapacity_{0}".format(d))
    return mdl

def define_distance_measures(mdl):
    # ----------------------------------------------------------------------- #
    # Minimize patient transfers
    # ----------------------------------------------------------------------- #   
    mdl.nb_long_transfers = mdl.sum(mdl.x_vars[d1, d2, t] 
                                for d1 in mdl.deps 
                                for d2 in mdl.deps 
                                if mdl.is_long[d1][d2] 
                                for t in mdl.transfer_periods)
    
    mdl.nb_short_transfers = mdl.sum(mdl.x_vars[d1, d2, t] 
                                 for d1 in mdl.deps 
                                 for d2 in mdl.deps 
                                 if not mdl.is_long[d1][d2] 
                                 for t in mdl.transfer_periods)
    
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
                         w_total_undercapacity = 100,
                         w_max_under = 100,
                         w_max_over = 1, 
                         w_nb_patient_transfers = 1,
                         w_km_patient_transfers = 0.01,
                         w_nb_long_transfers = 0.01):
    
    # ----------------------------------------------------------------------- #
    # Summarize all
    # ----------------------------------------------------------------------- #   
    mdl.minimize(w_total_undercapacity   * mdl.total_undercapacity +\
                 w_max_under             * mdl.max_under + \
                 w_max_over              * mdl.max_over + \
                 w_nb_patient_transfers  * mdl.nb_patient_transfers + \
                 w_km_patient_transfers  * mdl.km_patient_transfers + \
                 w_nb_long_transfers     * mdl.nb_long_transfers)
    return mdl