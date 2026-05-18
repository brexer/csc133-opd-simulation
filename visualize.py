import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

scenarios = {
    "S1 (Baseline)": "scenario_1_baseline_results.csv",
    "S2 (Appts)": "scenario_2_appointments_results.csv",
    "S3 (Priority)": "scenario_3_dynamic_priority_results.csv",
    "S4 (+1 Doc)": "scenario_4_resource_scaling_results.csv",
    "S5 (Combined)": "scenario_5_combined_results.csv"
}

urgent_waits = []
vuln_waits = []
reg_waits = []
labels = []

print("Analyzing Priority Breakdown...")

for name, filename in scenarios.items():
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df['Total_Wait'] = df['Wait_Registration'] + df['Wait_Triage'] + df['Wait_Consultation']
        
        # Group the math by the Priority Tag
        grouped = df.groupby('Priority_Tag')['Total_Wait'].mean()
        
        urgent_waits.append(grouped.get('Urgent', 0))
        vuln_waits.append(grouped.get('Vulnerable', 0))
        reg_waits.append(grouped.get('Regular', 0))
        labels.append(name)

x = np.arange(len(labels))
width = 0.2

fig, ax = plt.subplots(figsize=(12, 6))
bar1 = ax.bar(x - width, urgent_waits, width, label='Urgent', color='#e74c3c')
bar2 = ax.bar(x, vuln_waits, width, label='Vulnerable', color='#f39c12')
bar3 = ax.bar(x + width, reg_waits, width, label='Regular', color='#3498db')

ax.set_ylabel('Average Wait Time (Minutes)', fontsize=12)
ax.set_title('Wait Times by Priority Tier (All 5 Scenarios)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

plt.tight_layout()
plt.savefig('chapter_4_priority_breakdown_full.png', dpi=300)
print("\nSuccess! Full 5-scenario breakdown graph saved.")
plt.show()