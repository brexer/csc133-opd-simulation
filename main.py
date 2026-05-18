import pandas as pd
from model import ClinicModel

def run_monte_carlo(scenario_name, use_appts, use_priority, doctors, replications=1000, ticks_per_day=600):
    """
    The main Monte Carlo execution loop.
    ticks_per_day = 600 represents a 10-hour clinic shift (60 minutes * 10 hours).
    """
    print(f"\n--- Starting {scenario_name} ---")
    print(f"Config: Appts={use_appts}, Priority={use_priority}, Doctors={doctors}")
    all_results = []

    for i in range(replications):
        model = ClinicModel(use_appointments=use_appts, 
                            use_dynamic_priority=use_priority, 
                            num_doctors=doctors)

        for _ in range(ticks_per_day):
            model.step()

        # Extract the data logged by Mesa (in model.py) for this specific day
        daily_data = model.datacollector.get_agent_vars_dataframe()
        
        # Tag the data so we know which replication (day) it came from
        daily_data['Replication_ID'] = i 
        all_results.append(daily_data)

        if (i + 1) % 5 == 0:
            print(f"Completed {i + 1} / {replications} simulation days")

    # Aggregate all days into one Pandas DataFrame
    print(f"Aggregating data for {scenario_name}...")
    final_df = pd.concat(all_results)

    # Export to CSV
    filename = f"{scenario_name.replace(' ', '_').lower()}_results.csv"
    final_df.to_csv(filename)
    print(f"Simulation Complete. Data exported to {filename}")

if __name__ == "__main__":
    REPLICATIONS = 1000

    # Scenario 1: Baseline (FCFS Walk-ins)
    run_monte_carlo("Scenario 1 Baseline", use_appts=False, use_priority=False, doctors=3, replications=REPLICATIONS)

    # Scenario 2: Appointments Only (No Priority Sorting)
    run_monte_carlo("Scenario 2 Appointments", use_appts=True, use_priority=False, doctors=3, replications=REPLICATIONS)

    # Scenario 3: Dynamic Priority Routing Only
    run_monte_carlo("Scenario 3 Dynamic Priority", use_appts=False, use_priority=True, doctors=3, replications=REPLICATIONS)

    # Scenario 4: Resource Scaling (+1 Doctor)
    run_monte_carlo("Scenario 4 Resource Scaling", use_appts=False, use_priority=False, doctors=4, replications=REPLICATIONS)

    # Scenario 5: The Combined Strategy
    run_monte_carlo("Scenario 5 Combined", use_appts=True, use_priority=True, doctors=4, replications=REPLICATIONS)

    print("\nAll Scenarios Completed Successfully!")