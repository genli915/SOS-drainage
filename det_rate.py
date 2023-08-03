import numpy as np
import ruptures as rpt
import pandas as pd
from scipy import stats
import sys

# This function takes in the data and the dates and gives out the breakpoints in date
# Uses Ruptures Pelt for offline calculations
def get_breakpoints(dates, data):
	# print(data)
	# Use mean shift as change detection model
	model = "clinear"
	algo = rpt.Pelt(model=model, min_size=3).fit(data)

	# Detect the change points
	# Need to play around with pen
	# This outputs the indicies of the data where a breakpoint has been identified
	result = algo.predict(pen=2)
	# result = [num - 2 for num in result]
	# The last value in the array is the length of the array, so the length of dates need to be increased by 1
	dates.append(dates[-1])
	# This is the dates plus the last date
	change_points = [dates[idx] for idx in result]
	change_points[-1] = dates[-1]
	return change_points

# This function is to find the date in the list which is between the current and last dates
# If there is no value, return the last date
def earlier_next_date(current_date, dates_list, last_date):
	n = len(dates_list)
	min_date = last_date
	for x in range(n):
		if dates_list[x] < min_date and dates_list[x] > current_date:
			min_date = dates_list[x]

	return min_date

# Given the start and end dates, create new arrays for the corresponding dates and data
def data_within_range(start_date, end_date, dates_list, data):
	n = len(data)
	dates = []
	sd = []
	for x in range(n):
		if dates_list[x] >= start_date and dates_list[x] < end_date:
			dates.append(dates_list[x])
			sd.append(data[x])
	return dates, sd

# Get the slope using linear regression
def get_slope2(sd_dates_list, sd_list):
	slope, intercept, r, p, std_err = stats.linregress(sd_dates_list, sd_list)
	return slope

# This function should be used to get a list of geokeys within the range of the cluster
def get_geokeys(cluster_start_yards, cluster_end_yards, geokey_data, geokey_start_yards, geokey_end_yards):
	# Find a list of geokeys that has the range within what is required
	geokeys = []
	n = len(geokey_data)
	for x in range(n):
		if geokey_start_yards[x] >= cluster_start_yards and geokey_end_yards[x] <= cluster_end_yards:
			geokeys.append(geokey_data[x])
	
	# Return result
	return geokeys

def identify_outliers(x, y, threshold=3):
    # Calculate z-scores for x and y
    z_scores_x = np.abs((x - np.mean(x)) / np.std(x))
    z_scores_y = np.abs((y - np.mean(y)) / np.std(y))
    
    # Find outliers based on the threshold
    outlier_indices = np.where((z_scores_x > threshold) | (z_scores_y > threshold))[0]
    
    return outlier_indices

def remove_indices(lst, indices):
    indices = set(indices)  # Convert indices to a set for efficient membership checking
    return [elem for i, elem in enumerate(lst) if i not in indices]

# This function is used to find the number of overlaps of the data
def find_overlaps(dates_list, start_yards, end_yards, start_yards_list, end_yards_list, occurance_date):
	count = 0
	n = len(occurance_date)
	for x in range(n):
		if start_yards >= start_yards_list[x] and end_yards <= end_yards_list[x] and occurance_date[x] >= dates_list[0] and occurance_date[x] <= dates_list[-1]:
			count = count+1
	return count


# Read the spreadsheet
data = pd.read_excel(r'SU TQ.xlsx', sheet_name = "SU TQ")
# Get the sd data and its dates
sd_data = pd.DataFrame(data, columns=['wt35']).to_numpy()
date_data = pd.DataFrame(data, columns=['recdate']).to_numpy()
yid_list = pd.DataFrame(data, columns=['Yards ID']).to_numpy()
# start_yards_sd_data = pd.DataFrame(data, columns=['Start yards']).to_numpy()
# end_yards_sd_data = pd.DataFrame(data, columns=['End yards']).to_numpy()

# Do the same but for a different sheet
data = pd.read_excel(r'SU TQ.xlsx', sheet_name = "Yards ID")
geokey_data = pd.DataFrame(data, columns=['Yards ID']).to_numpy()
geokey_start_yards = pd.DataFrame(data, columns=['Start yards']).to_numpy()
geokey_end_yards = pd.DataFrame(data, columns=['End yards']).to_numpy()
# count_data = pd.DataFrame(data, columns=['Count of recdate']).to_numpy()

# Read the spreadsheet for drainage conditions
data = pd.read_excel(r'yid.xlsx')
start_yards_yid = pd.DataFrame(data, columns=['Start yards']).to_numpy()
end_yards_yid = pd.DataFrame(data, columns=['End yards']).to_numpy()
dates_yid = pd.DataFrame(data, columns=['Date']).to_numpy()
yards_id = pd.DataFrame(data, columns=['Yards ID']).to_numpy()
drainage_type = pd.DataFrame(data, columns=['Drainage Type']).to_numpy()

# Read the spreadsheet for wetbed occurances
data = pd.read_excel(r'Wet beds python.xlsx')
wetbed_dates = pd.DataFrame(data, columns=['Creation Date']).to_numpy()
wetbed_start_yards = pd.DataFrame(data, columns=['Start yards']).to_numpy()
wetbed_end_yards = pd.DataFrame(data, columns=['End yards']).to_numpy()

det_rate = []
count_datapoints = []
start_yards_output = []
yards_id_output = []
type_output = []
date_output = []
wetbeds_count = []

n = len(start_yards_yid)
print(n)

for x in range(n):
	# Add a value to det rate
	det_rate.append(None)
	count_datapoints.append(0)
	start_yards_output.append(start_yards_yid[x].item())
	yards_id_output.append(yards_id[x].item())
	type_output.append(drainage_type[x].item())
	date_output.append(dates_yid[x].item())
	wetbeds_count.append(0)

	# Save the number of datapoints and det_rate of each geokey with the same yards
	yid_sizes = []
	yid_det_rate = []

	# First create a list of the dates and data of that geokey
	l = len(sd_data)
	dates = []
	sd = []
	for y in range(l):
		# Go through the entire SU TQ to find the yid that match that of what we require
		# Then find its associated date and sd
		if yid_list[y] == yards_id[x]:
			dates.append(date_data[y].item())
			sd.append(sd_data[y].item())

	# Check the length of the data
	if len(sd) <= 5:
		continue

	# Now we have all the dates and sd date for the given geokey
	breakpoint_dates = get_breakpoints(dates, np.array(sd))

	# Find the end of the period we are looking for
	current_date = dates_yid[x]
	next_date = earlier_next_date(current_date, breakpoint_dates, current_date+365)

	# Create a list of all the dates and sd between the given dates
	new_dates, new_sd = data_within_range(current_date, next_date, dates, sd)

	length = len(new_sd)
	count_datapoints[x] = length

	# If the length of the data is too small
	if length < 5:
		continue

	outliers = identify_outliers(new_dates, new_sd)

	new_dates= remove_indices(new_dates, outliers)
	new_sd = remove_indices(new_sd, outliers)

	# Times 365 to get annual det rate
	det_rate[x] = get_slope2(new_dates, new_sd)*365
	wetbeds_count[x] = find_overlaps(new_dates, start_yards_yid[x].item(), start_yards_yid[x].item(), wetbed_start_yards, wetbed_end_yards, wetbed_dates)

# Output to a spreadsheet
data = pd.DataFrame({"Start yards": start_yards_output, "Count of datapoints": count_datapoints, "Slope": det_rate, "Yards ID": yards_id_output, "Drainage Type": type_output, "Drain measure date": date_output, "Wetbeds": wetbeds_count})
data.to_excel("Slope9.xlsx")