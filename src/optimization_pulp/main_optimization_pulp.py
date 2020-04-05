# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 08:59:33 2020
@author: tilda.lundgren
"""

def run_optimization(start_day="2020-4-3", 
                     time_horizon=3, 
                     path_to_trend_data = "../../src/forecast/forecast.csv",
                     path_to_static_region_data = "../../data/regions.csv",
                     path_to_static_geojson = "../../data/geocounties.geojson",
                     path_to_static_distances = "../../data/distances.pickle",
                     solve_time_limit = 60, #seconds
                     w_overcap_abs = 1,
                     w_overcap_rel = 1,
                     w_nb_trans = 1,
                     w_km_trans = 1
                     ):
    
    # --------------------------------------------------------------------------- #
    # Set-up
    # --------------------------------------------------------------------------- #  
    import warnings
    warnings.filterwarnings("ignore")
    
    from datetime import timedelta
    from datetime import datetime
    
    today = datetime.strptime(start_day, '%Y-%m-%d')
    target_day = today + timedelta(days=time_horizon)
    
    # --------------------------------------------------------------------------- #
    # Read data
    # --------------------------------------------------------------------------- #  
    from src.optimization_pulp import read_data_for_optimization_pulp 
    current_df, trend_dict = read_data_for_optimization_pulp.read_and_process_data(trend_data = path_to_trend_data,
                                                                              region_data = path_to_static_region_data,
                                                                              today = today)
    initial_map = read_data_for_optimization_pulp.plot_initial_state(current_df,geojson=path_to_static_geojson)    
    
    # --------------------------------------------------------------------------- #
    # Build and prepare optimization model
    # --------------------------------------------------------------------------- # 
    import pulp as plp
    from src.optimization_pulp import build_optimization_model_pulp
    mdl = build_optimization_model_pulp.build_model()
    mdl = build_optimization_model_pulp.define_model_parameters_and_sets(mdl, current_df)
    mdl = build_optimization_model_pulp.define_model_variables(mdl)
    mdl = build_optimization_model_pulp.calculate_distances(mdl, current_df,path_to_static_distances)
    
    from src.optimization_pulp import define_model_constraints_pulp
    mdl = define_model_constraints_pulp.exempt_departments(mdl)
    mdl = define_model_constraints_pulp.set_initial_state(mdl,current_df)
    mdl = define_model_constraints_pulp.link_x_and_y_vars(mdl)
    mdl = define_model_constraints_pulp.restrict_transfers(mdl)
    mdl = define_model_constraints_pulp.transfer_bounds(mdl)
    mdl = define_model_constraints_pulp.maximum_long_transfers(mdl)
    mdl = define_model_constraints_pulp.short_transfers_per_dep(mdl)
    mdl = define_model_constraints_pulp.update_for_next_period(mdl,trend_dict,today,target_day)
    
    from src.optimization_pulp import define_model_objective_pulp
    mdl = define_model_objective_pulp.define_max_overcapacity(mdl,current_df)
    mdl = define_model_objective_pulp.define_distance_measures(mdl)
    mdl = define_model_objective_pulp.summarize_objectives(mdl,
                                                           w_overcap_abs = w_overcap_abs,
                                                           w_overcap_rel = w_overcap_rel,
                                                           w_nb_trans = w_nb_trans,
                                                           w_km_trans = w_km_trans)
    
    # --------------------------------------------------------------------------- #
    # Solve model
    # --------------------------------------------------------------------------- # 
    import time
    start = time.time()
    mdl.solve(solver=plp.PULP_CBC_CMD());
    #mdl.solve(solver=plp.CPLEX(msg=False));
    end = time.time()
    print("Time to solve:",round(end-start,10),"seconds")
    
    # --------------------------------------------------------------------------- #
    # Process solution
    # --------------------------------------------------------------------------- # 
    from src.optimization_pulp import process_solution_pulp
    mdl = process_solution_pulp.process_allocations(mdl)
    mdl,current_df = process_solution_pulp.process_final_data(mdl,current_df,trend_dict,today,target_day)
    final_map_without_opt = process_solution_pulp.plot_final_state_without_opt(mdl,current_df,geojson=path_to_static_geojson)
    final_map = process_solution_pulp.plot_final_state(mdl,current_df,geojson=path_to_static_geojson)
    
    return initial_map, final_map, final_map_without_opt, mdl.allocation_plan