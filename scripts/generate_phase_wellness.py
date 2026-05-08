import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def compute_risk(sleep=7, stress=5, anxiety=5, activity=30, water=2.5, gender='Female', cycle_day=14):
    sw = (stress/10)*35
    sd = max(0, min(100, (8-sleep)/8*100)); slw = sd*0.25
    aw = (anxiety/10)*20
    ad = max(0, min(100, (60-activity)/60*100)); actw = ad*0.10
    wd = max(0, min(100, (2.5-water)/2.5*100)); ww = wd*0.05
    pm = 0
    if gender=='Female':
        if cycle_day<=5: pm=5
        elif cycle_day<=13: pm=-5
        elif cycle_day<=16: pm=-8
        else: pm=8
    return min(100, max(0, sw+slw+aw+actw+ww+5+pm))

# Definitions
phases = ['Menstrual\n(Days 1-5)','Follicular\n(Days 6-13)','Ovulatory\n(Days 14-16)','Luteal\n(Days 17-28)']
# Days representing each phase
test_days = [3, 10, 15, 22]
# Calculate wellness (100 - risk)
phase_wellness = [100 - compute_risk(gender='Female', cycle_day=d) for d in test_days]

fig, ax = plt.subplots(figsize=(8, 5))

# Colors representing different wellness levels or phases
colors = ['#e74c3c', '#2ecc71', '#3498db', '#f39c12'] 

bars = ax.bar(phases, phase_wellness, color=colors, edgecolor='white', width=0.6)
ax.bar_label(bars, fmt='%.1f', padding=5, fontweight='bold', fontsize=11)

ax.set_title('Phase-wise Wellness Comparison', fontweight='bold', fontsize=14, pad=20)
ax.set_ylabel('Estimated Wellness Score (0-100)', fontsize=12)
ax.set_ylim(0, 100)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
out_path = '/Users/prashantkumar/Desktop/Luna_Aura/paper_assets/phase_wise_wellness.png'
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Graph saved to {out_path}")
