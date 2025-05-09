import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

data = # attribute value scores 

# Labels
players = # [f'Player {i+1}' for i in range(len(data))]
attributes = # insert attributes here

col_labels = ["General", "Offensive", "Defensive", 
              "Mental & Visionary", "Goalkeeping", 
              "Potential/rating ratio (x100)"]
df = pd.DataFrame(data, index=players, columns=col_labels)

plt.figure(figsize=(10, 6))
sns.heatmap(df, annot=True, fmt=".0f", cmap="Greens", cbar_kws={"label": "Attribute value"}, linewidths=.5, linecolor='black')

plt.xlabel("Attributes")
plt.ylabel("Players (ordered based on rating)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
