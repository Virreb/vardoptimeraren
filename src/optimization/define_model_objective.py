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

def summarize_objectives(mdl):
    # ----------------------------------------------------------------------- #
    # Summarize all
    # ----------------------------------------------------------------------- #   
    mdl.minimize(100   * mdl.total_undercapacity +\
                 100   * mdl.max_under + \
                 1     * mdl.max_over + \
                 1     * mdl.nb_patient_transfers + \
                 0.01  * mdl.km_patient_transfers + \
                 0.01  * mdl.nb_long_transfers)
    return mdl