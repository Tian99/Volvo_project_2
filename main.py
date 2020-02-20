import os
import re
import numpy as np
import pandas as pd
from color_codings import color_collections
from commonlize import normalize_and_export, color_encoding



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
