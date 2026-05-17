import pandas as pd
from model import ClinicModel

def run_monte_carlo(replications=10, ticks_per_day=600):
    """
    The main Monte Carlo execution loop.
    ticks_per_day = 600 represents a 10-hour clinic shift (60 minutes * 10 hours).
    """
    print(f"Starting Monte Carlo Simulation: {replications} Replications")
    all_results = []

    for i in range(replications):
        model = ClinicModel()

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
    print("Aggregating synthetic data")
    final_df = pd.concat(all_results)

    # Export to CSV
    filename = "scenario_1_baseline_results.csv"
    final_df.to_csv(filename)
    print(f"Simulation Complete. Data exported to {filename}")

if __name__ == "__main__":
    run_monte_carlo(replications=1000)