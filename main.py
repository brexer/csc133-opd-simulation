"""
Monte Carlo replication engine for the OPD ABM Simulation.
Runs N replications of each of the 5 experimental scenarios and writes
two CSV files per scenario:
  - <scenario>_results.csv  : per-agent wait/service metrics
  - <scenario>_queues.csv   : per-minute queue length snapshots
"""

import pandas as pd
from model import ClinicModel

SCENARIOS = [
    {
        "name":        "Scenario 1 Baseline",
        "slug":        "scenario_1_baseline",
        "use_appts":   False,
        "use_priority": False,
        "doctors":     3,
    },
    {
        "name":        "Scenario 2 Appointments",
        "slug":        "scenario_2_appointments",
        "use_appts":   True,
        "use_priority": False,
        "doctors":     3,
    },
    {
        "name":        "Scenario 3 Dynamic Priority",
        "slug":        "scenario_3_dynamic_priority",
        "use_appts":   False,
        "use_priority": True,
        "doctors":     3,
    },
    {
        "name":        "Scenario 4 Resource Scaling",
        "slug":        "scenario_4_resource_scaling",
        "use_appts":   False,
        "use_priority": False,
        "doctors":     4,
    },
    {
        "name":        "Scenario 5 Combined",
        "slug":        "scenario_5_combined",
        "use_appts":   True,
        "use_priority": True,
        "doctors":     4,
    },
]
 
TICKS_PER_DAY = 600

def run_monte_carlo(scenario: dict, replications: int = 1000):
    """
    Runs `replications` independent days of the given scenario.
    Writes two CSV files and returns (agent_df, queue_df) for optional
    in-memory use.
    """
    name = scenario["name"]
    slug = scenario["slug"]
 
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"  Appts={scenario['use_appts']} | Priority={scenario['use_priority']} "
          f"| Doctors={scenario['doctors']}")
    print(f"{'='*60}")
 
    all_agent_results = []
    all_queue_results = []
 
    for i in range(replications):
        model = ClinicModel(
            use_appointments=scenario["use_appts"],
            use_dynamic_priority=scenario["use_priority"],
            num_doctors=scenario["doctors"],
            seed=i,          # deterministic per replication, comparable across scenarios
        )
 
        for _ in range(TICKS_PER_DAY):
            model.step()
 
        # agent-level data
        agent_df = model.datacollector.get_agent_vars_dataframe()
        agent_df = agent_df.groupby(level="AgentID").last().reset_index()
        agent_df["Replication_ID"] = i
        all_agent_results.append(agent_df)
 
        # model-level data
        queue_df = model.datacollector.get_model_vars_dataframe()
        queue_df.reset_index(names=["Minute"], inplace=True)
        queue_df["Replication_ID"] = i
        all_queue_results.append(queue_df)
 
        if (i + 1) % 100 == 0:
            print(f"  Completed {i + 1} / {replications} replications")
 
    print(f"  Aggregating and saving {name}...")
 
    final_agent_df = pd.concat(all_agent_results, ignore_index=True)
    agent_filename = f"{slug}_results.csv"
    final_agent_df.to_csv(agent_filename, index=False)
    print(f"  Saved → {agent_filename}")
 
    final_queue_df = pd.concat(all_queue_results, ignore_index=True)
    queue_filename = f"{slug}_queues.csv"
    final_queue_df.to_csv(queue_filename, index=False)
    print(f"  Saved → {queue_filename}")
 
    return final_agent_df, final_queue_df
 
if __name__ == "__main__":
    REPLICATIONS = 1000
 
    for scenario in SCENARIOS:
        run_monte_carlo(scenario, replications=REPLICATIONS)
 
    print("\n" + "=" * 60)
    print("  All 5 Scenarios Completed Successfully!")
    print("=" * 60)
 