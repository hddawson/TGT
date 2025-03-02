import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.lines import Line2D

# Load data
data = pd.read_csv("data/compiled_hobo_data_tgt6.csv")
print("Unique devices:", data['device'].nunique())

# Convert 'time' to datetime and then to hours since start
data['time'] = pd.to_datetime(data['time'])
data['time'] = (data['time'] - data['time'].min()).dt.total_seconds() / 3600

start_time = 2655  # in hours
end_time   = 3164  # in hours

# Filter data within the specified time frame
filtered_data = data[(data['time'] >= start_time) & (data['time'] <= end_time)]

# Compute 'hour' (relative to midnight; using the same -8 offset as before) and 'day'
filtered_data['hour'] = (filtered_data['time'] - 8) % 24
filtered_data['day']  = ((filtered_data['time'] - 8) // 24).astype(int)

# Create a new column for sensor type based on device:
def sensor_type(device):
    if device in ["B09", "B10", "B19", "B20"]:
        return 'soil-air-interface'
    else:
        return '1" depth'

filtered_data['sensor_type'] = filtered_data['device'].apply(sensor_type)

# Now group by gusset, sensor_type, and hour to compute the mean temperature and standard error (SEM)
grouped = filtered_data.groupby(['gusset', 'sensor_type', 'hour']).agg(
    mean_temp = ('temp', 'mean'),
    std_temp  = ('temp', 'std'),
    n         = ('temp', 'count')
).reset_index()
grouped['sem']   = grouped['std_temp'] #/ np.sqrt(grouped['n'])
grouped['lower'] = grouped['mean_temp'] - grouped['sem']
grouped['upper'] = grouped['mean_temp'] + grouped['sem']

# Define unique gusset values and sensor types
unique_gussets = sorted(filtered_data['gusset'].unique())
sensor_types   = grouped['sensor_type'].unique()

# Create a color mapping for gusset values using a qualitative colormap (here tab10)
cmap = plt.cm.get_cmap('Dark2', len(unique_gussets))
gusset_color_map = {gusset: cmap(i) for i, gusset in enumerate(unique_gussets)}

# Create legend handles for gusset colors
gusset_handles = [mpatches.Patch(color=gusset_color_map[g], label=f"Gusset {g}")
                  for g in unique_gussets]

# Create legend handles for sensor types (line style distinguishes sensor type)
sensor_handles = [
    Line2D([0], [0], color='black', linestyle=':', label='Sensor at \nsoil-air-interface'),
    Line2D([0], [0], color='black', linestyle='-', label='Sensor at \n1" depth')
]

plt.figure(figsize=(12, 12))

# For each gusset and sensor type, plot the mean temperature and error swathe
for gusset in unique_gussets:
    for sensor in sensor_types:
        subset = grouped[(grouped['gusset'] == gusset) & (grouped['sensor_type'] == sensor)]
        if subset.empty:
            continue
        subset = subset.sort_values('hour')
        # Use ':' for soil-air-interface and '-' for 1" depth
        ls = ':' if sensor == 'soil-air-interface' else '-'
        plt.plot(subset['hour'], subset['mean_temp'],
                 color=gusset_color_map[gusset], linestyle=ls)
        plt.fill_between(subset['hour'], subset['lower'], subset['upper'],
                         color=gusset_color_map[gusset], alpha=0.3)

plt.xticks(range(0, 24, 1), rotation=45)
plt.yticks(range(-1, 12, 1))
plt.xlabel("Hour (since midnight)")
plt.ylabel("Mean Temperature (°C)")
plt.title("Mean Temperature by Hour per Gusset with ± St. Dev.")

# Combine legends: one for gusset colors and one for sensor types (line style)
all_handles = gusset_handles + sensor_handles
plt.legend(handles=all_handles, bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid()
plt.tight_layout()
plt.savefig("plots/mean_temp_by_gusset_sensor_with_error_swathe.pdf")
plt.show()
plt.clf()
