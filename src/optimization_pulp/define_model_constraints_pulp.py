# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 09:23:21 2020
@author: tilda.lundgren
"""
import pulp as plp

def exempt_departments(mdl):
    # ----------------------------------------------------------------------- #
    # Exempt regions (will not recieve not patients)
    # ----------------------------------------------------------------------- #
    
    for d in mdl.EXEMPT: 
        for t in mdl.transfer_periods:
            mdl.addConstraint(plp.LpConstraint(e=plp.lpSum(mdl.y_vars[dx, d, t] for dx in mdl.deps),
                                               sense=plp.LpConstraintEQ,
                                               rhs=0,
                                               name="exempt_regions_{0}_{1}".format(d, t)))
    return mdl

def set_initial_state(mdl,current_df):
    # ----------------------------------------------------------------------- #           
    # Set initial state
    # ----------------------------------------------------------------------- #
    for d in mdl.deps:
        mdl.addConstraint(plp.LpConstraint(e=mdl.o_vars[d, 0],
                                           sense=plp.LpConstraintEQ,
                                           rhs=current_df.at[d,"IVA"],
                                           name="initial_state_{0}".format(d)))
    return mdl
        
def link_x_and_y_vars(mdl):
    # ----------------------------------------------------------------------- #
    # Structural constraint between x_vars and y_vars
    # ----------------------------------------------------------------------- #
    for pair in ((d1, d2) for d1 in mdl.deps for d2 in mdl.deps):
        for t in mdl.transfer_periods:
            mdl.addConstraint(plp.LpConstraint(e=mdl.y_vars[pair[0],pair[1],t] - mdl.MAX_CASES_PER_LONG_TRANSFERS * mdl.x_vars[pair[0],pair[1],t],
                                               sense=plp.LpConstraintLE,
                                               rhs=0,
                                               name="use_link_{0}_{1}_{2}".format(pair[0], pair[1], t)))
    return mdl

def restrict_transfers(mdl):
    # ----------------------------------------------------------------------- #
    # Number of transfers from a department should be less than patients
    # ----------------------------------------------------------------------- #
    for d in mdl.deps: 
        for t in mdl.transfer_periods:
            mdl.addConstraint(plp.LpConstraint(e=plp.lpSum(mdl.y_vars[d, dx, t] for dx in mdl.deps) - mdl.o_vars[d,t],
                                               sense=plp.LpConstraintLE,
                                               rhs=0,
                                               name="transfer_less_than_current_cases_{0}_{1}".format(d,t)))
    return mdl

def transfer_bounds(mdl):
    # ----------------------------------------------------------------------- #
    # Short/long transfers bounds
    # ----------------------------------------------------------------------- #
    for pair in ((d1, d2) for d1 in mdl.deps for d2 in mdl.deps):
        
        if mdl.is_long[pair[0]][pair[1]]:
            bound = mdl.MAX_CASES_PER_LONG_TRANSFERS
        else: 
            bound = mdl.MAX_CASES_PER_SHORT_TRANSFERS
        
        for t in mdl.transfer_periods:
            mdl.addConstraint(plp.LpConstraint(e=mdl.y_vars[pair[0],pair[1],t],
                                               sense=plp.LpConstraintLE,
                                               rhs=bound,
                                               name="transfer_bound_{0}_{1}_{2}".format(pair[0],pair[1],t)))
    return mdl

def maximum_long_transfers(mdl):
    # ----------------------------------------------------------------------- #
    # Maximum number of LONG transfers per period
    # ----------------------------------------------------------------------- #        
    for t in mdl.transfer_periods:
        long_transfers = plp.lpSum(mdl.x_vars[d1, d2, t] 
                                 for d1 in mdl.deps 
                                 for d2 in mdl.deps 
                                 if mdl.is_long[d1][d2])
        mdl.addConstraint(plp.LpConstraint(e=long_transfers,
                                           sense=plp.LpConstraintLE,
                                           rhs=mdl.MAX_NB_LONG_TRANSFERS_PER_PERIOD,
                                           name="max_long_transfers_{0}".format(t)))        
    return mdl

def short_transfers_per_dep(mdl):
    # ----------------------------------------------------------------------- #
    # Maximum number of SHORT transfers per department
    # ----------------------------------------------------------------------- #  
    for d in mdl.deps:
        short_transfers = plp.lpSum(mdl.x_vars[dx, d, t] 
                                  for dx in mdl.deps 
                                  if not mdl.is_long[dx][d] 
                                  for t in mdl.transfer_periods)
        mdl.addConstraint(plp.LpConstraint(e=short_transfers,
                                           sense=plp.LpConstraintLE,
                                           rhs=mdl.MAX_NB_SHORT_TRANSFERS_PER_DEPARTMENT,
                                           name="max_short_transfers_{0}".format(d)))  
    return mdl         
        
def update_for_next_period(mdl,trend_dict,today,target_day):
    # ----------------------------------------------------------------------- #
    # Update number of cases for next period
    # ----------------------------------------------------------------------- #     
    for d in mdl.deps:
        for t in mdl.transfer_periods:
            
            # Calculate existing cases and reallocations
            existing_cases = mdl.o_vars[d, t] 
            cases_in = plp.lpSum(mdl.y_vars[dx, d, t] for dx in mdl.deps)
            cases_out = plp.lpSum(mdl.y_vars[d, dx, t] for dx in mdl.deps)
          
            # Get prognosis for organic growth
            prognosis = trend_dict[d][trend_dict[d]["Date"] == target_day].IVA.values[0]
            current = trend_dict[d][trend_dict[d]["Date"] == today].IVA.values[0]
            organic_growth = prognosis - current #Prediction for organic growth goes here 
            
            #Summarize new cases
            new_cases = existing_cases + cases_in - cases_out + organic_growth
            
            # Add constraint
            mdl.addConstraint(plp.LpConstraint(e=mdl.o_vars[d, t+1] - new_cases,
                                               sense=plp.LpConstraintEQ,
                                               rhs=0,
                                               name="new_cases_{0}_{1}".format(d,t)))
    return mdl