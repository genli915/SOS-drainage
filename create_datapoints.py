import numpy as np
import ruptures as rpt
import pandas as pd
from scipy import stats

# Read the spreadsheet
data = pd.read_excel(r'SU TQ.xlsx', sheet_name = "SU TQ")
# Get the sd data and its dates
sd_data = pd.DataFrame(data, columns=['wt35']).to_numpy()
date_data = pd.DataFrame(data, columns=['recdate']).to_numpy()
geokey_list = pd.DataFrame(data, columns=['Yards ID']).to_numpy()
# start_yards_sd_data = pd.DataFrame(data, columns=['Start yards']).to_numpy()
# end_yards_sd_data = pd.DataFrame(data, columns=['End yards']).to_numpy()

# Do the same but for a different sheet
data = pd.read_excel(r'SU TQ.xlsx', sheet_name = "Yards ID")
yid_data = pd.DataFrame(data, columns=['Yards ID']).to_numpy()
yid_start_yards = pd.DataFrame(data, columns=['Start yards']).to_numpy()
yid_end_yards = pd.DataFrame(data, columns=['End yards']).to_numpy()
# count_data = pd.DataFrame(data, columns=['Count of recdate']).to_numpy()

# Read the spreadsheet for drainage conditions
data = pd.read_excel(r'Clusters_cleaned_3.xlsx', sheet_name = 'Data')
start_yards_clusters = pd.DataFrame(data, columns=['Start yards']).to_numpy()
end_yards_clusters = pd.DataFrame(data, columns=['End yards']).to_numpy()
cluster_dates = pd.DataFrame(data, columns=['Date']).to_numpy()
type_cluster = pd.DataFrame(data, columns=['Drainage Type']).to_numpy()
# conditions = pd.DataFrame(data, columns=['Drainage Service Condition']).to_numpy()


# Each start yards could have multiple data points due to up/down
# Create a new start yards list that could contain all the data
start_yards = []
end_yards = []
yid = []
date = []
type_cl = []
n = len(start_yards_clusters)
for x in range(n):
	m = len(yid_data)
	for y in range(m):
		if yid_start_yards[y] >= start_yards_clusters[x] and yid_end_yards[y] <= end_yards_clusters[x]:
			start_yards.append(start_yards_clusters[x])
			end_yards.append(end_yards_clusters[x])
			yid.append(yid_data[y])
			date.append(cluster_dates[x])
			type_cl.append(type_cluster[x])

	print(x)

data = pd.DataFrame({"Start yards": start_yards, "End yards": end_yards, "Yards ID": yid, "Date": date, "Drainage Type": type_cl})
data.to_excel("yid.xlsx")
			