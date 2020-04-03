# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 08:59:33 2020
@author: tilda.lundgren
"""

def run_optimization():
    
    # --------------------------------------------------------------------------- #
    # Set-up
    # --------------------------------------------------------------------------- #  
    import warnings
    warnings.filterwarnings("ignore")
    
    from datetime import timedelta
    from datetime import date
    today = date(2020,3,29) #today = date.today()
    target_day = today + timedelta(days=3)
    
    
    # --------------------------------------------------------------------------- #
    # Read data
    # --------------------------------------------------------------------------- #  
    import read_data_for_optimization 
    current_df, trend_dict = read_data_for_optimization.read_and_process_data(trend_data = "../../data/iva_kumulativ.csv",
                                                                          region_data = "../../data/regions.csv",
                                                                          today = today)
    folium_map = read_data_for_optimization.plot_initial_state(current_df)
    folium_map.save('initial_state.html')
    
    
    # --------------------------------------------------------------------------- #
    # Build and prepare optimization model
    # --------------------------------------------------------------------------- # 
    import build_optimization_model
    build_optimization_model.check_environment()
    mdl = build_optimization_model.build_model()
    mdl = build_optimization_model.define_model_parameters_and_sets(mdl, current_df)
    mdl = build_optimization_model.define_model_variables(mdl)
    mdl = build_optimization_model.calculate_distances(mdl, current_df)
    
    import define_model_constraints
    mdl = define_model_constraints.exempt_departments(mdl)
    mdl = define_model_constraints.set_initial_state(mdl,current_df)
    mdl = define_model_constraints.link_x_and_y_vars(mdl)
    mdl = define_model_constraints.restrict_transfers(mdl)
    mdl = define_model_constraints.transfer_bounds(mdl)
    mdl = define_model_constraints.maximum_long_transfers(mdl)
    mdl = define_model_constraints.short_transfers_per_dep(mdl)
    mdl = define_model_constraints.update_for_next_period(mdl,trend_dict,today,target_day)
    
    import define_model_objective
    mdl = define_model_objective.define_total_undercapacity(mdl,current_df)
    mdl = define_model_objective.undercapacity_distribution(mdl,current_df)
    mdl = define_model_objective.overcapacity_distribution(mdl,current_df)
    mdl = define_model_objective.define_distance_measures(mdl)
    mdl = define_model_objective.summarize_objectives(mdl)
    
    
    # --------------------------------------------------------------------------- #
    # Solve model
    # --------------------------------------------------------------------------- # 
    mdl.set_time_limit(60); #Seconds
    mdl.parameters.mip.strategy.probe.set(0);
    mdl.parameters.parallel.set(-1); #  opportunistic parallel search mode
    mdl.parameters.threads.set(4);
    mdl.solve(log_output=False,lex_mipgaps = [0.001])
    
    print("\nOptimal solution values:")
    print("Total undercapacity:", mdl.total_undercapacity.solution_value, "patients")
    print("Max region undercapacity:", mdl.max_under.solution_value, "patients")
    print("Max region overcapacity: ",mdl.max_over.solution_value,"patients")
    print("Patient transfers:",mdl.nb_patient_transfers.solution_value,"patients")
    print("Transfer kilometers:", round(mdl.km_patient_transfers.solution_value), "km")
    print("Long transfers:",mdl.nb_long_transfers.solution_value)
    print("Short transfers:",mdl.nb_short_transfers.solution_value)
    
    
    # --------------------------------------------------------------------------- #
    # Process solution
    # --------------------------------------------------------------------------- # 
    import process_solution
    mdl = process_solution.process_allocations(mdl)
    mdl,current_df = process_solution.process_final_data(mdl,current_df,trend_dict,today,target_day)
    folium_map = process_solution.plot_final_state(mdl,current_df)
    folium_map.save('final_state.html')