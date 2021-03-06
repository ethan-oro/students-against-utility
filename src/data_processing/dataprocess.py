## Data tools to process school data

# sys imports
import sys, os, shutil, errno

# string/data inputs
import string, csv, json, fileinput

# gucci imports
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

# misc
import progressbar
import collections
import pickle #for saving data objects


def main():
	print ("main")
	school_data = load_csv('../../data/massachusetts-public-schools-data/MA_Public_Schools_2017.csv')
	scraped_data = load_csv('../../scraper/econ_full_scrape_11-17-2018.csv')
	school_process(school_data, scraped_data)
	## want a dictionary of index to school code

def grab_data(output_metric = '% Graduated'):
	school_data = load_csv('../../data/massachusetts-public-schools-data/MA_Public_Schools_2017.csv')
	scraped_data = load_csv('../../scraper/econ_full_scrape_11-17-2018.csv')
	return school_process(school_data, scraped_data, output_metric)

def grab_data_spend():
	school_data = load_csv('../../data/massachusetts-public-schools-data/MA_Public_Schools_2017.csv')
	scraped_data = load_csv('../../scraper/econ_full_scrape_11-17-2018.csv')
	return spending_process(school_data, scraped_data)

def grab_data_full():
	school_data = load_csv('../../data/massachusetts-public-schools-data/MA_Public_Schools_2017.csv')
	scraped_data = load_csv('../../scraper/econ_full_scrape_11-17-2018.csv')
	return full_process(school_data, scraped_data)

def transform_data(dataframe_x, dataframe_y, train_split = 0.8, standardize = True):
	m,n = dataframe_x.shape

	x = np.array(dataframe_x)
	y = np.array(dataframe_y)
	random_state = np.random.get_state()
	np.random.shuffle(x)
	np.random.set_state(random_state)
	np.random.shuffle(y)
	split_ind = int(train_split*m)
	x_train = x[:split_ind,:]
	y_train = y[:split_ind]
	x_test = x[split_ind:,:]
	y_test = y[split_ind:]

	means = np.nanmean(x_train, axis=0)
	x_train = np.nan_to_num(x_train)
	x_test = np.nan_to_num(x_test)

	bad_inds_train = np.where(x_train == 0)
	bad_inds_test = np.where(x_test == 0)

	x_train[bad_inds_train] = np.take(means, bad_inds_train[1])
	x_test[bad_inds_test] = np.take(means, bad_inds_test[1])

	if standardize:
		normalizer = StandardScaler()
		x_train = normalizer.fit_transform(x_train)
		if train_split < 1.0:
			x_test = normalizer.transform(x_test)


	return (x_train, y_train, x_test, y_test)
def load_csv(filename):
	df = pd.read_csv(filename, sep =',')
	return df



def school_process(school_data, zip_data, output_metric = '% Graduated'):
	'''
	A. Split into elementary, middle, high schools

	'''
	school_categories = {
		'descriptive': ['School Code',
						'School Name',
						'Town',
						'State',
						'Zip',
						'District Name',
						'District Code'],
		'enrollment_by_grade': [
			'PK_Enrollment',
			'K_Enrollment',
			'1_Enrollment',
			'2_Enrollment',
			'3_Enrollment',
			'4_Enrollment',
			'5_Enrollment',
			'6_Enrollment',
			'7_Enrollment',
			'8_Enrollment',
			'9_Enrollment',
			'10_Enrollment',
			'11_Enrollment',
			'12_Enrollment',
			'SP_Enrollment',
		],
		'endogeneous_input': [
			'% First Language Not English',
			'% English Language Learner',
			'% Students With Disabilities',
			'% High Needs',
			'% Economically Disadvantaged',
			'% African American',
			'% Asian',
			'% Hispanic',
			'% White',
			'% Native American',
			'% Native Hawaiian, Pacific Islander',
			'% Multi-Race, Non-Hispanic',
			'% Males',
			'% Females',
			'Number of Students'
		],
		# 'exogeneous_input': [
		# 	'Total Expenditures',
		# 	'Average Expenditures per Pupil'
		# ],
		'exogeneous_input': [
			'Total # of Classes',
			'Average Class Size',
			'Salary Totals',
			'Average Salary',
			'FTE Count',
			'Total In-district FTEs',
			'Total Expenditures',
			'Total Pupil FTEs',
			'Average Expenditures per Pupil'
		],
		'output_markers': [
			'% Graduated',
			'% Attending College',
			'MCAS_10thGrade_Math_CPI',
			'MCAS_10thGrade_English_CPI',
			'Average SAT_Reading',
			'Average SAT_Writing',
			'Average SAT_Math'
		]
	}

	zip_categories = [
		'Median household income',
		'Avg Hours Worked',
		'Public Assistance and SSI',
		'Unemployment Rate',
		'Labor Force Participation',
		'Percent of Population In Poverty',
		'Public Assistance Percent',
		'Gini Index',
		'Single Earner Families',
		'Families with No One Working',
		'Avg Commute Time',
		'Self Employment Income',
		'Less Than Highschool in Poverty',
		'Local government',
		'State government'
	]
	aux_morn = [
		'12am to 5am',
		'5am to 530am',
		'530 am to 6am',
		'6am to 630am',
		'630 am to 7am',
		'7am to 730am',
		'730 am to 8am'
	]
	aux_eve = [
		'11am to 12noon',
		'12noon to 4pm',
		'4pm to midnight'
	]

	school_cols = school_categories['descriptive'] + school_categories['enrollment_by_grade'] + school_categories['endogeneous_input'] + school_categories['output_markers'] + school_categories['exogeneous_input']
	school_data = school_data[school_cols]
	school_data = school_data.rename(columns={'Zip':'Zip Code'})
	school_data = school_data.dropna()
	## Create Dummy Variables for School Type ##
	# one_hot_type = pd.get_dummies(school_data['School Type'])
	# school_data = school_data.join(one_hot_type)
	# school_data.drop('School Type', axis=1, inplace=True)
	#### Output Join Here ####

	zip_data['absent_morning'] = sum([zip_data[aux] for aux in aux_morn])
	zip_data['absent_evening'] = sum([zip_data[aux] for aux in aux_eve])

	zip_categories += ['absent_morning', 'absent_evening']
	zip_data = zip_data[zip_categories + ['Place']]

	zip_data = zip_data.rename(columns={'Place':'Zip Code'})
	## Join the zip code data with the school data ##
	joined = school_data.set_index('Zip Code').join(zip_data.set_index('Zip Code'), how='left', rsuffix='_scrape')

	## Normalization of numeric columns -- future work?##


	## Filter by school type -- bugs ##
	highschools = joined['12_Enrollment'] > 0
	middleschools = (joined['12_Enrollment'] == 0) & (joined['7_Enrollment'] > 0)
	elementaryschools = (joined['12_Enrollment'] == 0) & (joined['7_Enrollment'] == 0)

	## Filter the input and output columns
	x_cols = school_categories['endogeneous_input'] + school_categories['exogeneous_input'] + zip_categories # + ['Public School', 'Charter School']
	full_x = joined[x_cols]

	# output = joined['% Graduated']
	if output_metric == 'Composite MCAS CPI':
		joined['Composite MCAS CPI'] = joined['MCAS_10thGrade_Math_CPI'] + joined['MCAS_10thGrade_English_CPI']
	elif output_metric == 'Composite SAT':
		joined['Composite SAT'] = joined['Average SAT_Reading'] + joined['Average SAT_Writing'] + joined['Average SAT_Math']

	output = joined[output_metric]
	print (len(full_x[highschools]))
	print(len(highschools))
	data_dict = {
		'full_x': full_x,
		'full_y': output,
		'highschool_x': full_x[highschools],
		'highschool_y': output[highschools],
		'middleschool_x': full_x[middleschools],
		'middleschool_y': output[middleschools],
		'elementary_x': full_x[elementaryschools],
		'elementary_y': output[elementaryschools]
	}

	return data_dict

def spending_process(school_data, zip_data):
	'''
	A. Split into elementary, middle, high schools

	'''
	school_categories = {
		'descriptive': ['School Code',
						'School Name',
						'Town',
						'State',
						'Zip',
						'District Name',
						'District Code'],
		'enrollment_by_grade': [
			'PK_Enrollment',
			'K_Enrollment',
			'1_Enrollment',
			'2_Enrollment',
			'3_Enrollment',
			'4_Enrollment',
			'5_Enrollment',
			'6_Enrollment',
			'7_Enrollment',
			'8_Enrollment',
			'9_Enrollment',
			'10_Enrollment',
			'11_Enrollment',
			'12_Enrollment',
			'SP_Enrollment',
		],
		'endogeneous_input': [
			'% First Language Not English',
			'% English Language Learner',
			'% Students With Disabilities',
			'% High Needs',
			'% Economically Disadvantaged',
			'% African American',
			'% Asian',
			'% Hispanic',
			'% White',
			'% Native American',
			'% Native Hawaiian, Pacific Islander',
			'% Multi-Race, Non-Hispanic',
			'% Males',
			'% Females',
			'Number of Students'
		],
		'exogeneous_input': [
			'Total Expenditures',
			'Average Expenditures per Pupil'
		],
		'output_markers': [
			'Total # of Classes',
			'Average Class Size',
			'Salary Totals',
			'Average Salary',
			'FTE Count',
			'Total In-district FTEs',
			'Total Pupil FTEs'
		]
	}

	zip_categories = [
		'Median household income',
		'Avg Hours Worked',
		'Public Assistance and SSI',
		'Unemployment Rate',
		'Labor Force Participation',
		'Percent of Population In Poverty',
		'Public Assistance Percent',
		'Gini Index',
		'Single Earner Families',
		'Families with No One Working',
		'Avg Commute Time',
		'Self Employment Income',
		'Less Than Highschool in Poverty',
		'Local government',
		'State government'
	]

	output_categories = [
			'Total # of Classes',
			'Average Class Size',
			'Salary Totals',
			'Average Salary',
			'FTE Count',
			'Total In-district FTEs',
			'Total Pupil FTEs'
	]
	aux_morn = [
		'12am to 5am',
		'5am to 530am',
		'530 am to 6am',
		'6am to 630am',
		'630 am to 7am',
		'7am to 730am',
		'730 am to 8am'
	]
	aux_eve = [
		'11am to 12noon',
		'12noon to 4pm',
		'4pm to midnight'
	]

	school_cols = school_categories['descriptive'] + school_categories['enrollment_by_grade'] + school_categories['endogeneous_input'] + school_categories['exogeneous_input'] + school_categories['output_markers']
	school_data = school_data[school_cols]
	school_data = school_data.rename(columns={'Zip':'Zip Code'})
	school_data = school_data.dropna()
	## Create Dummy Variables for School Type ##
	# one_hot_type = pd.get_dummies(school_data['School Type'])
	# school_data = school_data.join(one_hot_type)
	# school_data.drop('School Type', axis=1, inplace=True)
	#### Output Join Here ####

	zip_data['absent_morning'] = sum([zip_data[aux] for aux in aux_morn])
	zip_data['absent_evening'] = sum([zip_data[aux] for aux in aux_eve])
	zip_categories += ['absent_morning', 'absent_evening']
	zip_data = zip_data[zip_categories + ['Place']]
	zip_data = zip_data.rename(columns={'Place':'Zip Code'})
	## Join the zip code data with the school data ##
	joined = school_data.set_index('Zip Code').join(zip_data.set_index('Zip Code'), how='left', rsuffix='_scrape')

	## Normalization of numeric columns -- future work?##


	## Filter by school type -- bugs ##
	highschools = joined['12_Enrollment'] > 0
	middleschools = (joined['12_Enrollment'] == 0) & (joined['7_Enrollment'] > 0)
	elementaryschools = (joined['12_Enrollment'] == 0) & (joined['7_Enrollment'] == 0)

	## Filter the input and output columns
	x_cols = school_categories['endogeneous_input'] + school_categories['exogeneous_input'] + zip_categories
	full_x = joined[x_cols]

	output = joined[output_categories]

	print (len(full_x[highschools]))
	data_dict = {
		'full_x': full_x,
		'full_y': output,
		'highschool_x': full_x[highschools],
		'highschool_y': output[highschools],
		'middleschool_x': full_x[middleschools],
		'middleschool_y': output[middleschools],
		'elementary_x': full_x[elementaryschools],
		'elementary_y': output[elementaryschools]
	}

	return data_dict

def full_process(school_data, zip_data):
	'''
	A. Split into elementary, middle, high schools

	'''
	school_categories = {
		'descriptive': ['School Code',
						'School Name',
						'Town',
						'State',
						'Zip',
						'District Name',
						'District Code'],
		'enrollment_by_grade': [
			'PK_Enrollment',
			'K_Enrollment',
			'1_Enrollment',
			'2_Enrollment',
			'3_Enrollment',
			'4_Enrollment',
			'5_Enrollment',
			'6_Enrollment',
			'7_Enrollment',
			'8_Enrollment',
			'9_Enrollment',
			'10_Enrollment',
			'11_Enrollment',
			'12_Enrollment',
			'SP_Enrollment',
		],
		'endogeneous_input': [
			'% First Language Not English',
			'% English Language Learner',
			'% Students With Disabilities',
			'% High Needs',
			'% Economically Disadvantaged',
			'% African American',
			'% Asian',
			'% Hispanic',
			'% White',
			'% Native American',
			'% Native Hawaiian, Pacific Islander',
			'% Multi-Race, Non-Hispanic',
			'% Males',
			'% Females',
			'Number of Students'
		],
		'exogeneous_input_first': [
			'Total Expenditures',
			'Average Expenditures per Pupil'
		],
		'intermediate': [
			'Total # of Classes',
			'Average Class Size',
			'Salary Totals',
			'Average Salary',
			'FTE Count',
			'Total In-district FTEs',
			'Total Pupil FTEs'
		],
		'output_markers': [
			# 'District_Progress and Performance Index (PPI) - All Students'
			'% Graduated'
			# '% Attending College'
		]
	}

	zip_categories = [
		'Median household income',
		'Avg Hours Worked',
		'Public Assistance and SSI',
		'Unemployment Rate',
		'Labor Force Participation',
		'Percent of Population In Poverty',
		'Public Assistance Percent',
		'Gini Index',
		'Single Earner Families',
		'Families with No One Working',
		'Avg Commute Time',
		'Self Employment Income',
		'Less Than Highschool in Poverty',
		'Local government',
		'State government'
	]

	aux_morn = [
		'12am to 5am',
		'5am to 530am',
		'530 am to 6am',
		'6am to 630am',
		'630 am to 7am',
		'7am to 730am',
		'730 am to 8am'
	]
	aux_eve = [
		'11am to 12noon',
		'12noon to 4pm',
		'4pm to midnight'
	]

	school_cols = school_categories['descriptive'] + school_categories['enrollment_by_grade'] + school_categories['endogeneous_input'] + school_categories['exogeneous_input_first'] + school_categories['intermediate'] + school_categories['output_markers']
	school_data = school_data[school_cols]
	school_data = school_data.rename(columns={'Zip':'Zip Code'})
	school_data = school_data.dropna()
	## Create Dummy Variables for School Type ##
	# one_hot_type = pd.get_dummies(school_data['School Type'])
	# school_data = school_data.join(one_hot_type)
	# school_data.drop('School Type', axis=1, inplace=True)
	#### Output Join Here ####

	zip_data['absent_morning'] = sum([zip_data[aux] for aux in aux_morn])
	zip_data['absent_evening'] = sum([zip_data[aux] for aux in aux_eve])
	zip_categories += ['absent_morning', 'absent_evening']
	zip_data = zip_data[zip_categories + ['Place']]
	zip_data = zip_data.rename(columns={'Place':'Zip Code'})
	## Join the zip code data with the school data ##
	joined = school_data.set_index('Zip Code').join(zip_data.set_index('Zip Code'), how='left', rsuffix='_scrape')

	## Normalization of numeric columns -- future work?##


	## Filter by school type -- bugs ##
	highschools = joined['12_Enrollment'] > 0
	middleschools = (joined['12_Enrollment'] == 0) & (joined['7_Enrollment'] > 0)
	elementaryschools = (joined['12_Enrollment'] == 0) & (joined['7_Enrollment'] == 0)

	## Filter the input and output columns
	always_x_cols = school_categories['endogeneous_input'] + zip_categories
	always_x = joined[always_x_cols]

	first_x_cols = school_categories['exogeneous_input_first']
	first_x = joined[first_x_cols]

	intermediate_cols  = school_categories['intermediate']
	intermediate = joined[intermediate_cols]

	second_output = joined['% Graduated']

	data_dict = {
		'always_x': always_x,
		'first_x': first_x,
		'intermediate': intermediate,
		'second_y': second_output,
		'highschool_always_x': always_x[highschools],
		'highschool_first_x': first_x[highschools],
		'highschool_intermediate': intermediate[highschools],
		'highschool_second_y': second_output[highschools],
		'middleschool_always_x': always_x[middleschools],
		'middleschool_first_x': first_x[middleschools],
		'middleschool_intermediate': intermediate[middleschools],
		'middleschool_second_y': second_output[middleschools],
		'elementaryschool_always_x': always_x[elementaryschools],
		'elementaryschool_first_x': first_x[elementaryschools],
		'elementaryschool_intermediate': intermediate[elementaryschools],
		'elementaryschool_second_y': second_output[elementaryschools]
	}

	return data_dict

if __name__ == '__main__':
	main()
