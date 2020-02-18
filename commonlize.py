import re
import os
import numpy as np
import pandas as pd
import pandas_profiling as pp
from pandas import ExcelWriter, ExcelFile

#####################Use this function as visualization
#df.discribe()
#Use this function ss visualization!!!
#######################This function split out any data that's with toxic naming convention

#Output the American side with data having the location information


def normalize(data_Bad):

	count = 0
	total_count = 0
	omitted = crucial = result = []
	free_result = toxic_result = pd.DataFrame()
	#On the loose end so that it could be more precise(Handle the space, the separation later)
	haRegex = re.compile("([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3})[/]([a-zA-Z]\d{1,3}|\d{1,3})")
	wrong_haRegex = re.compile("([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3})[*]([a-zA-Z]\d{1,3}|\d{1,3}|[a-zA-Z]+\s+\d{1,3})[*]([a-zA-Z]\d{1,3}|\d{1,3}|[a-zA-Z]+\s+\d{1,3})[*]([a-zA-Z]\d{1,3}|\d{1,3}|[a-zA-Z]+\s+\d{1,3}|[a-zA-Z]+\d{1,3}\s)[/](\s[a-zA-Z]+\d{1,3}|[a-zA-Z]\d{1,3}|\d{1,3}|[a-zA-Z]+\s+\d{1,3})")
	#Finding the need-changed expression from the already filtered expression
	detailed_find = re.compile("([a-zA-Z]\d{1,3}[/])|([a-zA-Z]+\s+\d{1,3}[/])|(\d{1,3}[/])")
	find_first = re.compile("([/]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3}))|([/]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3}))")
	first_sub = re.compile("[/]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]")

	exception = re.compile("[a-zA-Z]\d{1,3}[/](.*?)[/][a-zA-Z]\d{1,3}(?![^ ])")  
	# exception = re.compile("(([a-zA-Z]\d{1,3}[/])|([a-zA-Z]+\s+\d{1,3}[/])|(\d{1,3}[/]))[/](.*?)[/](([a-zA-Z]\d{1,3}[/])|([a-zA-Z]+\s+\d{1,3}[/])|(\d{1,3}[/]))")
	#Filter out the toxic dataset, later could do more filtering for the data leftovers.
	#Do it row by row
	for index, row in data_Bad.iterrows():
		total_count = total_count + 1
		print(total_count/len(data_Bad.index))
		#Those are four main target that should be looked into
		#May unclude comment field 1 later
		for i in [row['Comment Field 3'], row['Comment Field 2']]:
			origin_par = i
			i = i.replace(' ','')
			origin = 'Comment Field 3' if i == row['Comment Field 3'] else 'Comment Field 2'
			#Ignore anything with a / on the back
			if (re.search(haRegex, i)) and (re.search(wrong_haRegex, i) is None):
				#Start the surgery
				#Second degree filtering
				#Find the list of all the number replacing the first number
				if re.search(detailed_find, i) and re.search(find_first, i):
					count = count + 1
					print(count)
					#Replacements is a list contains all the replacement for the character located in the replaced which is a locaiton integer

					replacements = re.findall(detailed_find, i)
					replaced_loc = re.search(find_first, i).start()
					replaced = re.search(find_first, i).group(0)
					first = re.search(first_sub, replaced).group(0)
					for sample in replacements:
						#Replace the first char with every chars in the sample
						result.append(replaced.replace(first, str(sample[0]+sample[1]+'*')))
						print(sample)
					result.append(replaced)
					assignment = i + (str(result).replace('/', ''))
					#Trick way to assign data to the dataframe
					data_Bad.loc[data_Bad[origin] == origin_par, origin] = assignment

					print(assignment)
					print('\n\n')


				else:
					free_result = free_result.append(row)


			else:
				#Acceptable data
				free_result = free_result.append(row)
		result.clear()

	return data_Bad
	# free_result.to_excel('../output/free.xlsx')
	# print('to_excel successful')

def general_filtering(data):
	###################
	#First Level filtering
	#FIlter out the American side data
	data = data.loc[data['Vehicle Assembly Final Plant Code-Description'] == 'MT_93']
	print(len(data.index))

	###################
	###################
	#Second level filtering
	#Filter out trucks with location
	truck_with_loc = data[(data['Comment Field 2'].str.contains("\*")) | (data['Comment Field 3'].str.contains("\*"))]
	#Filter out trucks without locaiton information
	truck_without_loc = data[~((data['Comment Field 2'].str.contains("\*")) | (data['Comment Field 3'].str.contains("\*")))]

	print(len(truck_with_loc.index))
	print(len(truck_without_loc.index))

	return truck_with_loc, truck_without_loc
	####################

def filter_wrong_naming(truck_with_loc):
	####################
	#Third level filtering
	#Should mainly be working data_Bad
	data_Bad = truck_with_loc[data['Comment Field 3'].str.contains("/") | data['Comment Field 2'].str.contains("/")]
	# data_B_2 = data_missed.loc[data_missed['Comment Field 2'].str.contains("/")]
	#Data_free contains right formatted data=
	data_Free = truck_with_loc[~(data['Comment Field 3'].str.contains("/") | data['Comment Field 2'].str.contains("/"))]
	####################

	return data_Bad, data_Free

def normalize_and_export(data):
	truck_with_loc, truck_without_loc = general_filtering(data)
	data_Bad, data_Free = filter_wrong_naming(truck_with_loc)
	#Output the normalized data for dazta_Bad
	normalized = normalize(data_Bad)
	need_concat = [data_Free, normalized]
	#Start to merge
	merged = pd.concat(need_concat)
	print('Converting to excel now')
	# print(len(data.index))
	print(len(data_Bad.index))
	print(len(data_Free.index))
	print(len(merged.index))

	print(len(truck_without_loc.index))
	print(len(data.index))
	merged.to_excel('../output/normalized.xlsx')
	merged.to_pickle('../output/normalized.pkl')

	return merged

def color_collections():
	collection = {
		110:'Dent',
		112:'Broken',
		113:'Cut',
		114:'Puncture',
		118:'Stained/Soiled',
		119:'Missing',
		121:'Overspray',
		122:'Peel',
		123:'Gouge',
		125:'Poor/Repair',
		126:'Incorrect/Paint',
		155:'None',
		166:'None',
		171:'Rust',
		174:'None',
		182:'Crack',
		195:'Scratch',
		22:'None',
		64:'Chaffed/Rubbing',
		65:'Bent',
		92:'Run/Sag',
		93:'Dirt',
		94:'Fish/Eye/Solvent POP',
		96:'Orange/Peel',
		97:'Thin',
		98:'Paint/Mismatch',
} 
	return collection

def color_encoding(merged, collection):
	find_color = re.compile("([*]\d{1,3}[*])|([*]\d{1,3})|(\d{1,3}[*])")
	#Just directly do a search in string of all the row in dataframe since we've known the collection of numbders
	dye = []
	all_dye = []
	new_col = [[]]
	for index, row in merged.iterrows():
		for i in [row['Comment Field 3'], row['Comment Field 2']]:
			#First do a regular expression search just to make it more precise
			color_codings = re.findall(find_color, i)
			color_codings = str(color_codings)
			# color_codings = [s.strip('*') for s in color_codings]
			# print(color_codings)
			dye.append([value for key, value in collection.items() if str(key) in color_codings])

		#Merge the list as a whole to make it easier to analyze
		flatten = [item for sublist in dye for item in sublist]
		all_dye.append(flatten)
		dye.clear()
		print(flatten)
	print(len(all_dye))
	print(len(merged.index))
	merged = merged.assign(color_defect = all_dye)
	merged.to_excel('../output/finished.xlsx')
	print('Color coding finished')

collection = color_collections()
#Check if file exists
if os.path.isfile('../output/normalized.pkl'):
	print('the normalized data already existed, performing color coding')
	merged = pd.read_pickle('../output/normalized.pkl')
	color_encoding(merged, collection)
else: 
	print('the normalized data does not exist, performing normalization first then color coding')
	#Read the converted pickle file first
	data = pd.read_pickle('../data.pkl')
	merged = normalize_and_export(data)
	print('Data exported now, performing color coding')
	color_encoding(merged, collection)