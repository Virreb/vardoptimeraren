# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 08:59:33 2020
@author: tilda.lundgren
"""

def run_optimization(start_day="2020-3-28", 
                     time_horizon=3, 
                     path_to_trend_data = "../../data/iva_kumulativ.csv",
                     path_to_static_region_data = "../../data/regions.csv",
                     path_to_static_geojson = "../../data/geocounties.geojson",
                     path_to_static_distances = "../../data/distances.pickle",
                     solve_time_limit = 60, #seconds
                     w_total_undercapacity = 100,
                     w_max_under = 100,
                     w_max_over = 1,
                     w_nb_patient_transfers = 1,
                     w_km_patient_transfers = 0.01,
                     w_nb_long_transfers = 0.01
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
    import read_data_for_optimization_pulp 
    current_df, trend_dict = read_data_for_optimization_pulp.read_and_process_data(trend_data = path_to_trend_data,
                                                                              region_data = path_to_static_region_data,
                                                                              today = today)
    initial_map = read_data_for_optimization_pulp.plot_initial_state(current_df,geojson=path_to_static_geojson)    
    
    # --------------------------------------------------------------------------- #
    # Build and prepare optimization model
    # --------------------------------------------------------------------------- # 
    import pulp as plp
    import build_optimization_model_pulp
    mdl = build_optimization_model_pulp.build_model()
    mdl = build_optimization_model_pulp.define_model_parameters_and_sets(mdl, current_df)
    mdl = build_optimization_model_pulp.define_model_variables(mdl)
    mdl = build_optimization_model_pulp.calculate_distances(mdl, current_df,path_to_static_distances)
    
    import define_model_constraints_pulp
    mdl = define_model_constraints_pulp.exempt_departments(mdl)
    mdl = define_model_constraints_pulp.set_initial_state(mdl,current_df)
    mdl = define_model_constraints_pulp.link_x_and_y_vars(mdl)
    mdl = define_model_constraints_pulp.restrict_transfers(mdl)
    mdl = define_model_constraints_pulp.transfer_bounds(mdl)
    mdl = define_model_constraints_pulp.maximum_long_transfers(mdl)
    mdl = define_model_constraints_pulp.short_transfers_per_dep(mdl)
    mdl = define_model_constraints_pulp.update_for_next_period(mdl,trend_dict,today,target_day)
    
    import define_model_objective_pulp
    mdl = define_model_objective_pulp.define_max_overcapacity(mdl,current_df)
    mdl = define_model_objective_pulp.define_distance_measures(mdl)
    mdl = define_model_objective_pulp.summarize_objectives(mdl,
                                                      w_total_undercapacity = w_total_undercapacity,
                                                      w_max_under = w_max_under,
                                                      w_max_over = w_max_over,
                                                      w_nb_patient_transfers = w_nb_patient_transfers,
                                                      w_km_patient_transfers = w_km_patient_transfers,
                                                      w_nb_long_transfers = w_nb_long_transfers)
    
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
    import process_solution_pulp
    mdl = process_solution_pulp.process_allocations(mdl)
    mdl,current_df = process_solution_pulp.process_final_data(mdl,current_df,trend_dict,today,target_day)
    final_map_without_opt = process_solution_pulp.plot_final_state_without_opt(mdl,current_df,geojson=path_to_static_geojson)
    final_map = process_solution_pulp.plot_final_state(mdl,current_df,geojson=path_to_static_geojson)
    
    return initial_map, final_map, final_map_without_opt, mdl.allocation_plan