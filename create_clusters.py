# Using data from multiple spreadsheets, this code creates the clusters in a new spreadsheet

# Import
import pandas as pd
import numpy as np
import re
import find

# This function should require the data sets, the 220 yards section and classification (pipe, chamber or surface)
# It should return the earliest drainage condition with its date
# The drainage condition is the maximum (worst case) of any overlaps in the 220 yard section
# If there is no drainage condition measure, it returns 0 and 0/1/1900

def get_drainage_condition(drainage_start_yards, drainage_end_yards, conditions, measure_dates, classifications, yards_start, yards_end, classfication_req):
	# Create list where all numbers are larger than yards_start

	n = len(drainage_start_yards)
	index = []

	# Save the indexes (row numbers -2) of the data where the looped value has a starting point before the required end point
	for x in range(n):
		if yards_end >= drainage_start_yards[x] and yards_start <= drainage_end_yards[x] and classifications[x] == classfication_req:
			index.append(x)

	if index == []:
		return 0, 0

	# Initialise the earliest and next date and worst condition
	min_date = measure_dates[index[0]].item()
	# next_date = measure_dates[index[1]].item()
	max_condition = conditions[index[0]].item()
	max_condition_index = []

	# Find what is the worst drainage service condition
	for x in index:
		if max_condition < conditions[x]:
			max_condition = conditions[x].item()

	# Delete all indexes that are not worst conditions
	for x in index:
		if conditions[x] < max_condition:
			index.remove(x)

	# The index is now only those that have worst conditions
	# Now we need to find the earliest date
	for x in index:
		if min_date > measure_dates[x]:
			min_date = measure_dates[x].item()
	
	return max_condition, min_date

# Create the variables
paddington_yards = 0
bristol_yards = 197560
interval = 220

# Create a list for the start point (yards) of each section of rail
sections_start = list(range(paddington_yards, bristol_yards+1, interval))

# List of the end points of each section of rail
sections_end = [x+interval for x in sections_start]

# Open the drainage data excel file

# Read the spreadsheet
data = pd.read_excel(r'MLN1 SWB asset history with LatLong.xlsx', sheet_name = "MLN1 asset history with LatLong")

# Get the drainage data
drainage_start_yards = pd.DataFrame(data, columns=['Start yards']).to_numpy()
drainage_end_yards = pd.DataFrame(data, columns=['End yards']).to_numpy()
conditions_data = pd.DataFrame(data, columns=['Drainage Service Condition']).to_numpy()
measure_dates = pd.DataFrame(data, columns=['Date Of Measure']).to_numpy()
classifications = pd.DataFrame(data, columns=['Classification']).to_numpy()
side = pd.DataFrame(data, columns=['Side']).to_numpy()
# asset_id = pd.DataFrame(data, columns=['ID']).to_numpy

# print(classifications)

# For each section, obtain the drainage condition
condition = []
date = []
drainage_type = []
gradient = []
permeability = []
# id_no = []

n = len(sections_start)
y = 0

# These three for loop should really be in a function or something
# Record the conditions for chamber first
for x in range(n):
	# Make sure to add a element to the list so there is no error
	condition.append(0)
	date.append(0)
	drainage_type.append("Chamber")
	gradient.append(find.find_gradient(sections_start[x]+interval/2).item())
	condition[x], date[x] = get_drainage_condition(drainage_start_yards, drainage_end_yards, conditions_data, measure_dates, classifications, sections_start[x], sections_end[x], "Chamber")
	permeability.append(find.find_permeability(sections_start[x],sections_end[x]))
	print(x)

# print(classifications)

# Then for pipes
for x in range(n,2*n):
	condition.append(0)
	date.append(0)
	drainage_type.append("Pipe")
	gradient.append(find.find_gradient(sections_start[x-n]+interval/2).item())
	condition[x], date[x] = get_drainage_condition(drainage_start_yards, drainage_end_yards, conditions_data, measure_dates, classifications, sections_start[x-n], sections_end[x-n], "Pipe")
	permeability.append(find.find_permeability(sections_start[x-n],sections_end[x-n]))
	print(x)

# Then for surface
for x in range(2*n, 3*n):
	condition.append(0)
	date.append(0)
	drainage_type.append("Surface")
	gradient.append(find.find_gradient(sections_start[x-2*n]+interval/2).item())
	condition[x], date[x] = get_drainage_condition(drainage_start_yards, drainage_end_yards, conditions_data, measure_dates, classifications, sections_start[x-2*n], sections_end[x-2*n], "Surface")
	permeability.append(find.find_permeability(sections_start[x-2*n],sections_end[x-2*n]))
	print(x)


sections_start = sections_start + sections_start + sections_start
sections_end = sections_end + sections_end + sections_end

print(len(sections_start))
print(len(sections_end))
print(len(classifications))
print(len(condition))
print(len(date))

# Print to excel
cluster_data = pd.DataFrame({"Start yards": sections_start, "End yards": sections_end, "Drainage Type": drainage_type, "Drainage Service Condition": condition, "Date": date, "Gradient": gradient, "Permeability": permeability})

cluster_data.to_excel("Clusters.xlsx")