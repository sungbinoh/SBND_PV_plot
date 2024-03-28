import os
import psycopg2
from psycopg2 import Error
import matplotlib.pyplot as plt

connection = psycopg2.connect(user="<username>",
                                  password="<password>",
                                  host="sbnd-db01.fnal.gov",
                                  port="5434",
                                  database="sbnd_online_prd")

cursor = connection.cursor()
cursor.execute("set search_path to dcs_prd;")

#########################################################
# Time Window
#########################################################
### Example
##### start_timestamp = '2024-01-01 00:00:00'
##### end_timestamp = '2024-01-07 23:59:59'
start_timestamp = '2024-03-26 00:00:00'
end_timestamp = '2024-03-27 23:59:59'

#########################################################
# PV lists
#########################################################
PVs = ['sbnd_tpc_west_0_0/outputMeasurementCurrent', 'sbnd_tpc_west_0_2/outputMeasurementCurrent',
       'sbnd_tpc_west_0_5/outputMeasurementCurrent', 'sbnd_tpc_west_0_7/outputMeasurementCurrent',
       'sbnd_tpc_west_2_0/outputMeasurementCurrent', 'sbnd_tpc_west_2_1/outputMeasurementCurrent',
       'sbnd_tpc_west_2_2/outputMeasurementCurrent', 'sbnd_tpc_west_2_5/outputMeasurementCurrent']

# convert to channel ids
channel_ids = []
query_channel_id = "SELECT channel_id from channel where name =";
for PV in PVs:
    query_channel_id = "SELECT channel_id from channel where name = '" + PV + "';"
    cursor.execute(query_channel_id)
    channel_id = cursor.fetchall()[0][0]
    channel_ids.append(channel_id)

#########################################################
# Plot Settings
#########################################################
output_filename = 'MPOD_readback_currents.pdf'
plot_title = 'MPOD Read back Currents'
x_title = 'Time'
y_title = 'Current [nA]'

#########################################################
# Define the SQL query template
#########################################################
query_template = "SELECT smpl_time,float_val FROM sample WHERE channel_id = %s AND smpl_time BETWEEN %s AND %s"

#########################################################
# Collect date points
#########################################################
samples = []
for channel_id in channel_ids:
    cursor.execute(query_template, (channel_id,start_timestamp,end_timestamp,))
    this_data = cursor.fetchall()
    samples.append(this_data)

######################################################### 
# Plot PVs together
######################################################### 
plt.figure(figsize=(15, 6))
for i, data in enumerate(samples):
    datetimes = [item[0] for item in data]
    values = [item[1] for item in data]
    plt.plot(datetimes, values, marker='o', linestyle='-', label=PVs[i])

plt.title(plot_title);
plt.xlabel(x_title)
plt.ylabel(y_title)
plt.grid(True)
plt.tight_layout()
plt.legend()

# Format the x-axis to display dates
plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))
plt.xticks(rotation=45)

plt.subplots_adjust(bottom=0.3) 
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.tight_layout()

# Show the plot
plt.savefig(output_filename)
