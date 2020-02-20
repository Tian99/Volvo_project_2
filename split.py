import pandas as pd
import re

def find_answer(content):
	#Split the location informations from the words and from each other
	find = re.compile("(([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3}))|(([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3})[*]([a-zA-Z]\d{1,3}|[a-zA-Z]+\s+\d{1,3}|\d{1,3}))")

	#Get all the outcome from the regex
	answer = re.findall(find, content)
	#Narrow it down to getting the first element form the regex
	answer = [i[0] for i in answer]
	#Get rid of duplicates and return 
	return set(answer)

#the origional commonlize code is too messy, so start over would be a better option
def split(data):
	#Define a new dataframe structure
	tidy = pd.DataFrame()

	for index, row in data.iterrows():
		#Those are two main target that should be looked into
		for i in [row['Comment Field 3'], row['Comment Field 2']]:
			#Return an instance of set
			result = find_answer(content, i)

			for j in result: 
				row = row.assign(location_code = j)
				tidy.append(row)
		


				





