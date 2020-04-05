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
    from src.optimization import read_data_for_optimization
    current_df, trend_dict = read_data_for_optimization.read_and_process_data(trend_data = path_to_trend_data,
                                                                              region_data = path_to_static_region_data,
                                                                              today = today)
    initial_map = read_data_for_optimization.plot_initial_state(current_df,geojson=path_to_static_geojson)    
    
    # --------------------------------------------------------------------------- #
    # Build and prepare optimization model
    # --------------------------------------------------------------------------- # 
    from src.optimization import build_optimization_model
    build_optimization_model.check_environment()
    mdl = build_optimization_model.build_model()
    mdl = build_optimization_model.define_model_parameters_and_sets(mdl, current_df)
    mdl = build_optimization_model.define_model_variables(mdl)
    mdl = build_optimization_model.calculate_distances(mdl, current_df, path_to_static_distances)
    
    from src.optimization import define_model_constraints
    mdl = define_model_constraints.exempt_departments(mdl)
    mdl = define_model_constraints.set_initial_state(mdl,current_df)
    mdl = define_model_constraints.link_x_and_y_vars(mdl)
    mdl = define_model_constraints.restrict_transfers(mdl)
    mdl = define_model_constraints.transfer_bounds(mdl)
    mdl = define_model_constraints.maximum_long_transfers(mdl)
    mdl = define_model_constraints.short_transfers_per_dep(mdl)
    mdl = define_model_constraints.update_for_next_period(mdl,trend_dict,today,target_day)
    
    from src.optimization import define_model_objective
    mdl = define_model_objective.define_max_overcapacity(mdl,current_df)
    mdl = define_model_objective.define_distance_measures(mdl)
    mdl = define_model_objective.summarize_objectives(mdl,
                                                      w_overcap_abs = w_overcap_abs,
                                                      w_overcap_rel = w_overcap_rel,
                                                      w_nb_trans = w_nb_trans, 
                                                      w_km_trans = w_km_trans)
    
    # --------------------------------------------------------------------------- #
    # Solve model
    # --------------------------------------------------------------------------- # 
    mdl.set_time_limit(solve_time_limit); #Seconds
    mdl.parameters.mip.strategy.probe.set(0);
    mdl.parameters.parallel.set(-1); #  opportunistic parallel search mode
    mdl.parameters.threads.set(4);
    mdl.solve(log_output=False,lex_mipgaps = [0.001])    
    
    # --------------------------------------------------------------------------- #
    # Process solution
    # --------------------------------------------------------------------------- # 
    from src.optimization import process_solution
    mdl = process_solution.process_allocations(mdl)
    mdl,current_df = process_solution.process_final_data(mdl,current_df,trend_dict,today,target_day)
    final_map_without_opt = process_solution.plot_final_state_without_opt(mdl,current_df,geojson=path_to_static_geojson)
    final_map = process_solution.plot_final_state(mdl,current_df,geojson=path_to_static_geojson)
    
    return initial_map, final_map, final_map_without_opt, mdl.allocation_plan