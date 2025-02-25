import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

data = pd.read_csv("compiled_hobo_data.csv")

#how many unqiue devices are there?
print(data['device'].nunique())

# Convert the 'time' column to datetime format
data['time'] = pd.to_datetime(data['time'])

#convert the time column to hours from the start
data['time'] = (data['time'] - data['time'].min()).dt.total_seconds() / 3600

start_time = 470  # in hours
end_time = 770   # in hours

# Filter data within the specified time frame
filtered_data = data[(data['time'] >= start_time) & (data['time'] <= end_time)]

# Plot the filtered data
plt.figure(figsize=(30, 6))
for device, device_data in filtered_data.groupby('device'):
    plt.plot(device_data['time'], device_data['temp'], label=device)

# Rotate the x-axis labels
plt.xticks(rotation=45)

# Add more x ticks and a grid
plt.xticks(range(start_time, end_time + 1, 4))
plt.grid()
plt.ylabel('Temperature (°C)')
plt.title('HOBO Temperature Data (Limited Time Frame)')
plt.legend()
plt.savefig("plots/hobo_temperature_plot.pdf")

#clear the plot
plt.clf()

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

"""
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