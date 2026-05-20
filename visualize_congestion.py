"""
Generates the Peak Congestion line chart.
Shows average queue lengths at each minute of the shift,
averaged across all replications for a chosen scenario.

Run AFTER main.py has generated the queue CSV files.
Usage:
    python visualize_congestion.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import os

SCENARIO_SLUG  = "scenario_3_dynamic_priority"
SCENARIO_LABEL = "Scenario 3 (Dynamic Priority Routing)"
TICKS_PER_DAY  = 600

filename = f"{SCENARIO_SLUG}_queues.csv"

if not os.path.exists(filename):
    print(f"Error: {filename} not found. Run main.py first.")
    exit(1)

print(f"Analyzing peak congestion data for {SCENARIO_LABEL}...")

df = pd.read_csv(filename)

# Average queue length at each minute of the day across all replications
avg = df.groupby("Minute")[["Reg_Line", "Triage_Line", "Doctor_Line"]].mean()

# Also compute 95% CI band for Doctor_Line (the primary bottleneck)
std_err = df.groupby("Minute")["Doctor_Line"].std() / (
    df["Replication_ID"].nunique() ** 0.5
)
ci_upper = avg["Doctor_Line"] + 1.96 * std_err
ci_lower = (avg["Doctor_Line"] - 1.96 * std_err).clip(lower=0)

fig, ax = plt.subplots(figsize=(13, 6))

ax.plot(avg.index, avg["Reg_Line"],
        label="Registration Queue",   color="#2ecc71", linewidth=2)
ax.plot(avg.index, avg["Triage_Line"],
        label="Triage Queue",         color="#f39c12", linewidth=2)
ax.plot(avg.index, avg["Doctor_Line"],
        label="Doctor Queue (Bottleneck)", color="#e74c3c", linewidth=2.5)

# 95% CI band around the Doctor queue
ax.fill_between(avg.index, ci_lower, ci_upper,
                color="#e74c3c", alpha=0.15, label="Doctor Queue 95% CI")

ax.set_title(
    f"Average Hospital Congestion Over a 10-Hour Shift\n{SCENARIO_LABEL} "
    f"(1,000 Replications)",
    fontsize=13, fontweight="bold"
)
ax.set_xlabel("Time Elapsed (Minutes into Shift)", fontsize=12)
ax.set_ylabel("Number of Patients Waiting in Queue", fontsize=12)
ax.set_xlim(0, TICKS_PER_DAY)
ax.set_ylim(bottom=0)
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend(fontsize=10)

# Mark the peak congestion minute for the doctor queue
peak_minute = avg["Doctor_Line"].idxmax()
peak_value  = avg["Doctor_Line"].max()
ax.annotate(
    f"Peak: {peak_value:.1f} patients\n@ minute {peak_minute}",
    xy=(peak_minute, peak_value),
    xytext=(peak_minute + 30, peak_value + 0.5),
    arrowprops={"arrowstyle": "->", "color": "black"},
    fontsize=9, color="black"
)

plt.tight_layout()
output_file = f"chapter_4_peak_congestion_{SCENARIO_SLUG}.png"
plt.savefig(output_file, dpi=300)
print(f"Success! Congestion chart saved → {output_file}")
plt.show()