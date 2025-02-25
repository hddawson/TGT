import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Load the data
data = pd.read_csv("compiled_hobo_data.csv")

# Convert the 'time' column to datetime format
data['time'] = pd.to_datetime(data['time'])

# Convert the time column to hours from the start
data['time'] = (data['time'] - data['time'].min()).dt.total_seconds() / 3600

# Define the time frame (modify as needed)
start_time = 470  # in hours
end_time = 770    # in hours

# Filter data within the specified time frame
filtered_data = data[(data['time'] >= start_time) & (data['time'] <= end_time)]

# Plot the filtered data
plt.figure(figsize=(30, 6))

# Use a colormap (e.g., 'viridis', 'plasma', 'coolwarm')
cmap = plt.get_cmap("coolwarm")

# Normalize temperature values for color mapping
norm = plt.Normalize(filtered_data['temp'].min(), filtered_data['temp'].max())

# Plot each device with a temperature gradient
for device, device_data in filtered_data.groupby('device'):
    plt.scatter(
        device_data['time'], device_data['temp'], 
        c=device_data['temp'], cmap=cmap, norm=norm, s=10, label=device
    )

# Rotate the x-axis labels
plt.xticks(rotation=45)

# Add more x ticks and a grid
plt.xticks(range(start_time, end_time + 1, 4))
plt.grid()

# Colorbar to indicate temperature scale
cbar = plt.colorbar()
cbar.set_label("Temperature (°C)")

plt.ylabel('Temperature (°C)')
plt.title('HOBO Temperature Data (Colored by Temperature)')
plt.legend()
plt.savefig("plots/colormap_hobo_temperature_plot.pdf")
