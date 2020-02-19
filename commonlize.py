import re
import os
import numpy as np
import pandas as pd
import pandas_profiling as pp
from pandas import ExcelWriter, ExcelFile
from color_codings import color_collections

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
	#(/)+[character+number or character + space + number or number] + (*) + [character + number or character + space + number or number] + (*).......keep on going with the same pattern
	#Finding the main part ex: /A3*D4*45*3
	find_first = re.compile("([/]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3}))|([/]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3}))")
	#Right now simply exclude anything with a / in the back
	#f3*a3*c3*k5/a3
	wrong_haRegex = re.compile("([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3})[*]([a-zA-Z]\d{1,3}|\d{1,3}|[a-zA-Z]+\s+\d{1,3})[*]([a-zA-Z]\d{1,3}|\d{1,3}|[a-zA-Z]+\s+\d{1,3})[*]([a-zA-Z]\d{1,3}|\d{1,3}|[a-zA-Z]+\s+\d{1,3}|[a-zA-Z]+\d{1,3}\s)[/](\s[a-zA-Z]+\d{1,3}|[a-zA-Z]\d{1,3}|\d{1,3}|[a-zA-Z]+\s+\d{1,3})")
	#On the loose end so that it could be more precise(Handle the space, the separation later)
	#s4/d3
	haRegex = re.compile("([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3})[/]([a-zA-Z]\d{1,3}|\d{1,3})")
	#Finding the need-changed expression from the already filtered expression
	#a3/
	detailed_find = re.compile("([a-zA-Z]\d{1,3}[/])|([a-zA-Z]+\s+\d{1,3}[/])|(\d{1,3}[/])")
	#/a4*
	first_sub = re.compile("[/]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]")
	# exception = re.compile("[a-zA-Z]\d{1,3}[/](.*?)[/][a-zA-Z]\d{1,3}(?![^ ])")  
	# exception = re.compile("(([a-zA-Z]\d{1,3}[/])|([a-zA-Z]+\s+\d{1,3}[/])|(\d{1,3}[/]))[/](.*?)[/](([a-zA-Z]\d{1,3}[/])|([a-zA-Z]+\s+\d{1,3}[/])|(\d{1,3}[/]))")
	
	#Filter out the toxic dataset, later could do more filtering for the data leftovers.
	#Do it row by row
	for index, row in data_Bad.iterrows():
		total_count = total_count + 1
		print('Percentage of completion: ')
		print(total_count/len(data_Bad.index))
		#Those are four main target that should be looked into
		for i in [row['Comment Field 3'], row['Comment Field 2']]:
			#Keeop an origional version before the space is removed
			origin_par = i
			#Remove the space for each data set to increase the precision
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
	print('length of toxic data: %d',len(data_Bad.index))
	print('length of non-toxic data: %d',len(data_Free.index))
	print('length of data after merging: %d',len(merged.index))

	print('length of data without the location index: %d', len(truck_without_loc.index))
	print('length of data in total: %d', len(data.index))
	#Transform the solution to excel and to pickle
	merged.to_excel('../output/normalized.xlsx')
	merged.to_pickle('../output/normalized.pkl')

	return merged


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

#The main function where everything runs

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


