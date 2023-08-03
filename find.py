# This code is to be run more of a one off
# Each drainage measurement is a dataset so we need to obtain its gradient, soil permeability and number of trains

import pandas as pd

# Given a yards, output the gradient
def find_gradient(yards):
	# Read the spreadsheet
	data = pd.read_excel(r'Gradients MLN1 SWB.xlsx')
	# Get the yards data and gradient data
	yards_data = pd.DataFrame(data, columns=['Yards']).to_numpy()
	gradient_data = pd.DataFrame(data, columns=['Gradient']).to_numpy()
	# Direction data indicated "UP" or “DOWN" slope
	direction_data = pd.DataFrame(data, columns=['Direction']).to_numpy()

	# Find the length of the dataset
	n = len(yards_data)

	# Create a variable for the gradient
	gradient = None

	# For loop to find the gradient value
	for x in range(n):
		# Return the value if the yards is in the correct bracket
		if yards_data[x]<=yards and yards_data[x+1]>yards:
			if direction_data[x] == "DOWN":
				# Return from the function
				return gradient_data[x]*-1
			else:
				# Return from the function
				return gradient_data[x]

	# If nothing is returned, raise an error
	raise TypeError("Value not within the range of the data provided")


# Given a start and end yards, output the permeablity, when there is a mix, outputs the most common, when they are equal, output mixed
# If unknown, output unknown
def find_permeability(section_start, section_end):
	# Read the spreadsheet
	data = pd.read_excel(r'soil cuttings SU_work.xlsx', sheet_name = "soil cuttings SU")

	# Get the yards data and permeability data
	start_yards = pd.DataFrame(data, columns=['Start yards']).to_numpy()
	end_yards = pd.DataFrame(data, columns=['End yards']).to_numpy()
	permeability_data = pd.DataFrame(data, columns=['Permeability']).to_numpy()

	# Set up
	n = len(start_yards)
	permeable = 0
	impermeable = 0
	previous_perm = None
	next_perm = None
	#mixed = 0


	# Loop through the permeability data
	for x in range(n):
		# If the data says permeable, add the overlap distance onto the variable
		if permeability_data[x].item() == "Permeable":
			permeable = int(permeable + get_overlap(section_start, section_end, start_yards[x].item(), end_yards[x].item()))
			# print("a")

		# Same below
		elif permeability_data[x].item() == "Impermeable":
			impermeable = int(impermeable + get_overlap(section_start, section_end, start_yards[x].item(), end_yards[x].item()))

		# If it is the value immediately prior to the section required
		if end_yards[x].item() <= section_start and start_yards[x+1].item() >= section_end:
			previous_perm = permeability_data[x]
			next_perm = permeability_data[x+1]
			pass

	# If the dataset does not cover the required range
	if permeable == 0 and impermeable == 0:
		# If the permeability immediately before and after the range is the same, return that
		if previous_perm == next_perm and previous_perm != None:
			print("Same")
			return previous_perm

		# return "Unknown"

	# Output the most popular result
	if permeable >= impermeable:
		return "Permeable"

	if impermeable > permeable:
		return "Impermeable"

	# All other scenarios
	return "Unknown"


# This function returns the overlap distance between a and b
def get_overlap(a_start, a_end, b_start, b_end):

	# If b completely covers a, distance is a
	if a_start >= b_start and a_end <= b_end:
		# print('a')
		return a_end - a_start

	# If a completely covers b, distance is b
	if b_start >= a_start and b_end <= a_end:
		# print('b')
		return b_end - b_start
	
	# If not completely covered and start of a is inside b
	if b_end > a_start and b_start < a_start:
		# print('c')
		return b_end - a_start

	# If not completely covered and end of a is inside b
	if b_start < a_end and b_end > a_end:
		# print('d')
		return a_end - b_start

	# Otherwise the is no overlap, return 0
	return 0
