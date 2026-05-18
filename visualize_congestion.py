import pandas as pd
import matplotlib.pyplot as plt
import os

# We will look at Scenario 3, since that is your winning algorithm
filename = "scenario_3_dynamic_priority_queues.csv"

if os.path.exists(filename):
    print("Analyzing Peak Congestion Data...")
    df = pd.read_csv(filename)
    
    # We ran 1000 days. We need to find the AVERAGE queue length at each specific minute of the day.
    # Group by the 'Minute' column and calculate the mean for the lines.
    avg_congestion = df.groupby('Minute')[['Reg_Line', 'Triage_Line', 'Doctor_Line']].mean()

    # --- Draw the Line Chart ---
    plt.figure(figsize=(12, 6))
    
    plt.plot(avg_congestion.index, avg_congestion['Reg_Line'], label='Registration Queue', color='#2ecc71', linewidth=2)
    plt.plot(avg_congestion.index, avg_congestion['Triage_Line'], label='Triage Queue', color='#f39c12', linewidth=2)
    plt.plot(avg_congestion.index, avg_congestion['Doctor_Line'], label='Doctor Queue (Bottleneck)', color='#e74c3c', linewidth=3)
    
    # Format the graph
    plt.title('Average Hospital Congestion Over a 10-Hour Shift (Scenario 3)', fontsize=14, fontweight='bold')
    plt.xlabel('Time Elapsed (Minutes)', fontsize=12)
    plt.ylabel('Number of Patients Waiting in Lobby', fontsize=12)
    
    # Mark the start and end of the day clearly
    plt.xlim(0, 600)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('chapter_4_peak_congestion.png', dpi=300)
    print("Success! High-resolution congestion line graph saved.")
    plt.show()
else:
    print(f"Error: Could not find {filename}. Did you run main.py first?")