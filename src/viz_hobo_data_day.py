import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

data = pd.read_csv("data/compiled_hobo_data_tgt6.csv")

# How many unique devices are there?
print(data['device'].nunique())

# Convert the 'time' column to datetime format
data['time'] = pd.to_datetime(data['time'])

# Convert the time column to hours from the start
data['time'] = (data['time'] - data['time'].min()).dt.total_seconds() / 3600

start_time = 2655  # in hours
end_time = 3164    # in hours

# Filter data within the specified time frame
filtered_data = data[(data['time'] >= start_time) & (data['time'] <= end_time)]

# Determine the hour (out of 24 for each point) and day
filtered_data['hour'] = (filtered_data['time'] - 8) % 24
filtered_data['day'] = ((filtered_data['time'] - 8) // 24).astype(int)

# Create a color mapping for gusset values (assumed to be integers from 1 to 8)
unique_gussets = sorted(filtered_data['gusset'].unique())  # e.g., [1, 2, ..., 8]

# Use the Set1 colormap (designed for categorical data)
cmap = plt.cm.get_cmap('tab10', len(unique_gussets))
gusset_color_map = {gusset: cmap(i) for i, gusset in enumerate(unique_gussets)}

#print(gusset_color_map[1][0])

# Create custom legend handles for gusset colors
legend_handles = [mpatches.Patch(color=gusset_color_map[g], label=f"Gusset {g}")
                  for g in unique_gussets]

# Create an extra legend handle for dotted lines (sensor at soil-air-interface)
sensor_handle = Line2D([0], [0], color='black', linestyle=':', label='Sensor at \n soil-air-interface')
sensor_handle2 = Line2D([0], [0], color='black', linestyle='-', label='Sensor at \n 1" depth')

plt.figure(figsize=(10, 12))
# Group by device and day, then plot each time-series colored by its gusset value
for (device, day), group in filtered_data.groupby(['device', 'day']):
    # Assuming gusset is constant within each group:
    gusset_value = group['gusset'].iloc[0]
    if device in ["B09", "B10", "B19", "B20"]:
        plt.plot(group['hour'], group['temp'],
                 label=f"{device} (Day {day})",
                 linestyle=':',
                 color=gusset_color_map[gusset_value])
    else:
        plt.plot(group['hour'], group['temp'],
                 label=f"{device} (Day {day})",
                 linestyle='-',
                 color=gusset_color_map[gusset_value])

# Rotate the x-axis labels and add more x ticks and a grid
plt.xticks(range(0, 24, 1), rotation=45)
plt.grid()
plt.ylabel('Temperature (°C)')
plt.xlabel('Time of day (hours since midnight)')
plt.title('HOBO Temperature Data (21 Successive Days)')

# Combine the gusset legend handles and the sensor handle
all_handles = legend_handles + [sensor_handle] + [sensor_handle2]
plt.legend(handles=all_handles, bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.savefig("plots/day_hobo_temperature_plot_tgt6.pdf")
plt.show()


#clear the plot
plt.clf()
"""
#okay, now we want to split the data into two experiments
exp_1_start = 40
exp_1_end = 188
exp_2_start = 500
exp_2_end = 664

exp_1_data = data[(data['time'] >= exp_1_start) & (data['time'] <= exp_1_end)]
exp_2_data = data[(data['time'] >= exp_2_start) & (data['time'] <= exp_2_end)]

#for each of the 2 experiments, reset the time to start at 0
exp_1_data['time'] = exp_1_data['time'] - exp_1_data['time'].min()
exp_2_data['time'] = exp_2_data['time'] - exp_2_data['time'].min()

#and then we want to make a plot for each device where we overlay the temp from both experiments
# on each device

for device, device_data in data.groupby('device'):
    # Overlay data from experiment 1
    plt.figure(figsize=(12, 6))
    exp_1_device_data = exp_1_data[exp_1_data['device'] == device]
    plt.plot(exp_1_device_data['time'], exp_1_device_data['temp'], label=device + ' (Exp 1)')

    # Overlay data from experiment 2
    exp_2_device_data = exp_2_data[exp_2_data['device'] == device]
    plt.plot(exp_2_device_data['time'], exp_2_device_data['temp'], label=device + ' (Exp 2)')

    #finish and save the plot
    plt.xticks(rotation=45)
    plt.xticks(range(0, int(exp_2_device_data['time'].max()), 4))
    plt.grid()
    plt.ylabel('Temperature (°C)')
    plt.title('HOBO Temperature Data')
    plt.legend()

    plt.savefig(f"plots/{device}_temperature_plot_experiments.pdf")

#some of these hobos were in the same gusset in the trial, so we will also want to plot those together
# we can define a dictionary of gusset pairings
gusset_pairings = {
    1: ['B01', 'B11'],
    2: ['B02', 'B12'],
    3: ['B03', 'B13', 'B09', 'B19'],
    4: ['B04', 'B14'],
    5: ['B05', 'B15'],
    6: ['B06', 'B16', 'B10', 'B20'],
    7: ['B07', 'B17'],
    8: ['B08', 'B18'],
}

# Calculate rolling averages for each experiment

#drop B02 from exp 1 data and 2
exp_1_data = exp_1_data[exp_1_data['device'] != 'B02']
exp_2_data = exp_2_data[exp_2_data['device'] != 'B02']
#exp_1_data['rolling_temp'] = exp_1_data['temp'].rolling(window=10).mean()
#exp_2_data['rolling_temp'] = exp_2_data['temp'].rolling(window=10).mean()

# Calculate mean temperatures
exp_1_mean_temp = exp_1_data.groupby('time')['temp'].mean().reset_index()
exp_2_mean_temp = exp_2_data.groupby('time')['temp'].mean().reset_index()

# Plot mean table temperature with rolling average
plt.figure(figsize=(12, 6))
plt.plot(exp_1_mean_temp['time'], exp_1_mean_temp['temp'], label='Exp 1')
plt.plot(exp_2_mean_temp['time'], exp_2_mean_temp['temp'], label='Exp 2')
plt.xticks(rotation=45)
plt.grid()
plt.ylabel('Temperature (°C)')
plt.xlabel('Time (hours)')
plt.title('Mean Table Temperature with Average Across Experiments')
plt.legend()
plt.savefig("plots/mean_table_temperature_plot_experiments_no_rolling.pdf")


# Loop through each gusset pairing and plot the data, if available, reproducing the plots above but with all devices in one gusset overlain
for gusset, devices in gusset_pairings.items():
    plt.figure(figsize=(12, 6))

    for device in devices:
        # Data from experiment 1 for the current device
        exp_1_device_data = exp_1_data[exp_1_data['device'] == device]
        if not exp_1_device_data.empty:
            plt.plot(exp_1_device_data['time'], exp_1_device_data['temp'], label=f"{device} (Exp 1)")

        # Data from experiment 2 for the current device
        exp_2_device_data = exp_2_data[exp_2_data['device'] == device]
        if not exp_2_device_data.empty:
            plt.plot(exp_2_device_data['time'], exp_2_device_data['temp'], label=f"{device} (Exp 2)")

    # Finish and save the plot
    plt.xticks(rotation=45)
    plt.yticks(range(-4, 25, 1))
    plt.grid()
    plt.ylabel('Temperature (°C)')
    plt.xlabel('Time (hours)')
    plt.title(f'Gusset {gusset} Temperature Data Across Experiments')
    plt.legend()
    plt.savefig(f"plots/gusset_{gusset}_temperature_plot_experiments.pdf")
    plt.clf()
"""