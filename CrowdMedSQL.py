from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import pandas as pd

dbname = "patient"
username = "maksat"

#engine = create_engine('postgres://%s@localhost/%s'%(username,dbname))
engine = create_engine("postgresql+psycopg2:///%s?host=/var/run/postgresql"%(dbname))
print(engine.url)

#create an engine if doesn't already exist
if not database_exists(engine.url):
	create_database(engine.url)

print(database_exists(engine.url))

#load a database from CSV
#birth_data = pd.DataFrame.from_csv('births2012_downsampled.csv')

#open files
mds = pd.read_json('/home/maksat/Desktop/Insight/mds.json')
medcases = pd.read_json('/home/maksat/Desktop/Insight/medcases.json')
survey = pd.read_json('/home/maksat/Desktop/Insight/surveyanswers.json')

#change names
def getRating(row):
    for item in row:
        if item['key']=='rating':
            return int(item['value'])
def getInsight(row):
    for item in row:
        if item['key']=='insights':
            return item['value']
def getShare(row):
    for item in row:
        if item['key']=='share':
            return item['value']
        
survey['rating'] = survey.questions.apply(getRating)
survey['insight'] = survey.questions.apply(getInsight)
survey['share'] = survey.questions.apply(getShare)

import re
medcases['year'] = medcases['created'].apply(lambda x: re.findall(r'([0-9]+?)-',str(x))[0])

medCaseCols = ['_id','user','activityPercentile','medicationCount','lifestyle',
		#'medications','familyHistory','primaryBodySystem','primaryComplaint'
		#'priorDoctors',
		'symptoms',
		'caseDuration','costs','country','diseaseYear','ethnicity','year',
		'birthYear','reward','id','productivityLost','reported','resolved','state',
		'struggle','tests','timeSpent','surveyAnswered','gender']

surveyCols = ['_id','rating','insight','share']
mdsCols = ['_id','balance','cashWon']

#match = (survey['_id'] == survey['medcase'])
#print(survey[~match][['_id','medcase']])

survey['_id'] = survey['medcase']

surveyAndMedCase = pd.merge(survey[surveyCols],medcases[medCaseCols], on='_id')
surveyAndMedCase['_id'] = surveyAndMedCase['user']
#print(surveyAndMedCase.head(5))

surveyAndMedCase.pop('user')
allMerged = pd.merge(mds[mdsCols], surveyAndMedCase, on='_id')
allMerged['age'] = allMerged['diseaseYear'].astype(int)-allMerged['birthYear'].astype(int)
allMerged['waitYear'] = allMerged['year'].astype(int)-allMerged['diseaseYear'].astype(int)

## insert data into database from Python (proof of concept - this won't be useful for big data, of course)
## df is any pandas dataframe 
allMerged.to_sql('patient_survey_table', engine, if_exists='replace')

## Now try the same queries, but in python!
# connect:
con = None
con = psycopg2.connect(database = dbname, user = username)
# query:
sql_query = """
SELECT id FROM patient_survey_table WHERE age>30 OR share='Yes';
"""
data_from_sql = pd.read_sql_query(sql_query,con)
print(data_from_sql.head())
