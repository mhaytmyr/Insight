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

#open files
mds = pd.read_json('/home/maksat/Desktop/Insight/mds.json')
medcases = pd.read_json('/home/maksat/Desktop/Insight/medcases.json')
survey = pd.read_json('/home/maksat/Desktop/Insight/surveyanswers.json')

#general public informatrion
control = pd.read_csv('2014_consolidation.csv')

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


medCaseCols = ['_id','user','activityPercentile','medicationCount','lifestyle','priorDoctors',
		'symptoms','caseDuration','costs','country','diseaseYear','ethnicity','year',
		'birthYear','reward','id','productivityLost','reported','resolved','state',
		'struggle','tests','timeSpent','surveyAnswered','gender','bodySystemsString']

surveyCols = ['_id','rating','insight','share']
mdsCols = ['_id','balance','cashWon']

survey['_id'] = survey['medcase']

surveyAndMedCase = pd.merge(survey[surveyCols],medcases[medCaseCols], on='_id')
surveyAndMedCase['_id'] = surveyAndMedCase['user']

surveyAndMedCase.pop('user')
allMerged = pd.merge(mds[mdsCols], surveyAndMedCase, on='_id')
allMerged['age'] = allMerged['year'].astype(int)-allMerged['birthYear'].astype(int)
allMerged['waitYear'] = allMerged['year'].astype(int)-allMerged['diseaseYear'].astype(int)


def getBodyType(x):
    lst = []
    for item in str(x).split(','): 
        lst.append(''.join(item.lower().split(' ')))
    return ' '.join(lst)

allMerged = allMerged.dropna(subset=['costs'],how='any')
allMerged['costs'] = allMerged['costs'].apply(lambda x: int(x)/1000)
allMerged['insight'] = allMerged['insight'].apply(lambda x: True if str(x)=='Yes' else False)
allMerged['rating'] = allMerged['rating'].dropna().apply(lambda x: 1 if int(x)>2 else 0)
allMerged['bodySytemComplaint'] = allMerged['bodySystemsString'].apply(lambda x: getBodyType(x))
allMerged['bodyComplaintCnt'] = allMerged['bodySytemComplaint'].apply(
        lambda x: 0 if len(' '.join(x))<1 else len(x.split(' ')))


#now start control sample
genPop = pd.DataFrame()
genPop['age'] = control['AGELAST']
genPop['priorDoctors'] = control['ADAPPT42']
genPop['medicationCount'] = control['RXTOT14']
genPop['bodyComplaintCnt'] = control.shape[0]*0
genPop['waitYear'] = control.shape[0]*0
genPop['gender'] = control['SEX']
genPop['costs'] = control['TOTTCH14'].apply(lambda x: int(x)/1000)
sickness = {'HIBPDX':'HIBPAGED','CHDDX':'CHDAGED','ANGIDX':'ANGIAGED','MIDX':'MIAGED','OHRTDX':'OHRTAGED',
            'STRKDX':'STRKAGED','EMPHDX':'EMPHAGED','CHOLDX':'CHOLAGED','DIABDX':'DIABAGED',
            'ARTHDX':'ARTHAGED','ASTHDX':'ASTHAGED'}

for key in sickness:
    control[key] = control[key].apply(lambda x: 0 if int(x)!=1 else 1)
    control[sickness[key]] = control[sickness[key]].apply(lambda x: None if int(x)<0 else x)
    genPop['bodyComplaintCnt']+=control[key]
    genPop[sickness[key]] = control[sickness[key]]
    
genPop['waitYear'] = genPop['age']-genPop[[sickness[key] for key in sickness]].min(axis=1, skipna=True)
genPop = genPop[(genPop['bodyComplaintCnt']>0) & (genPop['priorDoctors']>0) & (genPop['waitYear']>0)]
genPop['rating'] = 0

features = ['priorDoctors','age','waitYear','medicationCount','costs','rating','bodyComplaintCnt','gender']

data = allMerged[features].dropna(subset=['costs','rating'],how='any')
bkg = genPop[features]
mergedDF = pd.concat([data,bkg])

## insert data into database from Python (proof of concept-this won't be useful for big data, of course)
## df is any pandas dataframe 
mergedDF.to_sql('patient_survey_table', engine, if_exists='replace')

## Now try the same queries, but in python!
# connect:
con = None
con = psycopg2.connect(database = dbname, user = username)
# query:
sql_query = """
SELECT "priorDoctors","medicationCount","waitYear","priorDoctors","gender" FROM patient_survey_table WHERE age>30 OR rating=1;
"""
data_from_sql = pd.read_sql_query(sql_query,con)
print(data_from_sql.head())
