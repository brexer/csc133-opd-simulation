"""
Generates the Priority Breakdown bar chart across all 5 scenarios.
Includes 95% confidence intervals derived from the 1,000 Monte Carlo replications.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

SCENARIOS = {
    "S1\n(Baseline)":   "scenario_1_baseline_results.csv",
    "S2\n(Appts)":      "scenario_2_appointments_results.csv",
    "S3\n(Priority)":   "scenario_3_dynamic_priority_results.csv",
    "S4\n(+1 Doc)":     "scenario_4_resource_scaling_results.csv",
    "S5\n(Combined)":   "scenario_5_combined_results.csv",
}

PRIORITY_TIERS   = ["Urgent", "Vulnerable", "Regular"]
TIER_COLORS      = {"Urgent": "#e74c3c", "Vulnerable": "#f39c12", "Regular": "#3498db"}
Z_95             = 1.96   # z-score for 95% confidence interval


def compute_stats(df: pd.DataFrame, tier: str):
    """
    Returns (grand_mean, ci_half_width) for Total_Wait of a priority tier.
    CI is computed across per-replication means (accounts for replication variance).
    """
    subset = df[df["Priority_Tag"] == tier]
    if subset.empty:
        return 0.0, 0.0

    per_rep = subset.groupby("Replication_ID")["Total_Wait"].mean()
    grand_mean = per_rep.mean()
    std_err = per_rep.std() / np.sqrt(len(per_rep))
    ci = Z_95 * std_err
    return grand_mean, ci

labels       = []
means        = {t: [] for t in PRIORITY_TIERS}
ci_widths    = {t: [] for t in PRIORITY_TIERS}

print("Analyzing Priority Breakdown...")

for label, filename in SCENARIOS.items():
    if not os.path.exists(filename):
        print(f"  WARNING: {filename} not found — skipping.")
        continue

    df = pd.read_csv(filename)
    df["Total_Wait"] = (
        df["Wait_Registration"] + df["Wait_Triage"] + df["Wait_Consultation"]
    )
    labels.append(label)

    for tier in PRIORITY_TIERS:
        m, ci = compute_stats(df, tier)
        means[tier].append(m)
        ci_widths[tier].append(ci)

if not labels:
    print("No data files found. Run main.py first.")
    exit(1)

x = np.arange(len(labels))
width = 0.22
offsets = {"Urgent": -width, "Vulnerable": 0, "Regular": width}

fig, ax = plt.subplots(figsize=(13, 7))

for tier in PRIORITY_TIERS:
    bars = ax.bar(
        x + offsets[tier],
        means[tier],
        width,
        yerr=ci_widths[tier],
        capsize=4,
        label=tier,
        color=TIER_COLORS[tier],
        alpha=0.88,
        error_kw={"elinewidth": 1.5, "ecolor": "black"},
    )
    for bar, mean_val in zip(bars, means[tier]):
        if mean_val > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(ci_widths[tier]) * 1.1 + 0.5,
                f"{mean_val:.1f}",
                ha="center", va="bottom", fontsize=7.5, color="black"
            )

ax.set_ylabel("Average Total Wait Time (Minutes)", fontsize=12)
ax.set_title(
    "Average Wait Time by Priority Tier Across All 5 Scenarios\n"
    "(1,000 Monte Carlo Replications — Error bars: 95% CI)",
    fontsize=13, fontweight="bold"
)
ax.set_xticks(x)
ax.set_xticklabels(labels, fontsize=10)
ax.legend(title="Priority Tier", fontsize=10, title_fontsize=10)
ax.yaxis.grid(True, linestyle="--", alpha=0.5)
ax.set_axisbelow(True)

plt.tight_layout()
output_file = "chapter_4_priority_breakdown_full.png"
plt.savefig(output_file, dpi=300)
print(f"\nSuccess! Chart saved → {output_file}")
plt.show()