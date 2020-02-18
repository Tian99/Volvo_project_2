import os
import pandas as pd
from pandas import ExcelFile
from pandas import ExcelWriter

def read(filename):
	data = pd.read_excel(filename)
	data.to_pickle('../data.pkl')
	print('finish converting')

read('../2019-12 Claims.xlsx') 
