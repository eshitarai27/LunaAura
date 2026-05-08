import matplotlib.pyplot as plt
import matplotlib.patches as patches

# PHQ-9 Categories and Ranges
categories = [
    ("Minimal", 0, 4, "#2ecc71"),
    ("Mild", 5, 9, "#f1c40f"),
    ("Moderate", 10, 14, "#e67e22"),
    ("Moderately Severe", 15, 19, "#e74c3c"),
    ("Severe", 20, 27, "#c0392b")
]

fig, ax = plt.subplots(figsize=(10, 3))
ax.set_xlim(0, 27)
ax.set_ylim(0, 1)

# Remove axes
ax.axis('off')

# Add the bars and text
for (name, start, end, color) in categories:
    width = end - start + 1
    rect = patches.Rectangle((start, 0), width, 0.5, facecolor=color, edgecolor='white', linewidth=2)
    ax.add_patch(rect)
    
    # Category text
    plt.text(start + width/2, 0.6, name, ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Range text
    plt.text(start + width/2, 0.25, f"{start}-{end}", ha='center', va='center', fontsize=12, color='white', fontweight='bold')

plt.title("PHQ-9 Depression Severity Ranges", fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()

# Save the figure
output_path = "/Users/prashantkumar/Desktop/Luna_Aura/paper_assets/phq9_range_visualization.png"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Visualization saved to {output_path}")
