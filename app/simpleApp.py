from app import app, simpleModel
from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
from flask import request
import psycopg2

user = 'maksat' #add your username here (same as previous postgreSQL)                      
host = 'localhost'
dbname = 'patient'
db = create_engine('postgres://%s%s/%s'%(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

@app.route('/')
@app.route('/printName')
def printName():
        return "Hi there Max"

@app.route('/simpleDB')
def id_Query():
        sql_query = """SELECT * FROM patient_survey_table WHERE age>30;"""

        query_results = pd.read_sql_query(sql_query,con)
        ids = ""
        for i in range(0,10):
                ids += query_results.iloc[i]['id'].astype(str)
                ids += "<br>"
        return ids

@app.route('/fancyDB')
def id_Query_Fancy():
        sql_query = """SELECT id,country,ethnicity FROM patient_survey_table WHERE age>30;"""
        query_results=pd.read_sql_query(sql_query,con)
        demography = []

        for i in range(0,query_results.shape[0]):
                demography.append(dict(index=query_results.iloc[i]['id'],
			country=query_results.iloc[i]['country'],
			ethnicity=query_results.iloc[i]['ethnicity']))

        return render_template('cesearian.html',births=demography)

@app.route('/input')
def input_page():
        return render_template("input.html")

@app.route('/output')
def output_page():
	#pull features from input field and store it
	patient = request.args.get('case_id')
	#write simple query
	#query = """
	#SELECT  age, gender,ethnicity,"priorDoctors","waitYear","medicationCount",costs FROM patient_survey_table WHERE age>'%s'
	#"""%patient

	query = """
	SELECT  age, gender,ethnicity,"priorDoctors","waitYear","medicationCount",costs,insight,reward FROM patient_survey_table WHERE id='%s'
	"""%patient

	query_results=pd.read_sql_query(query,con)

	query_list,features = [],[]
	for i in range(0,query_results.shape[0]):
		query_list.append(dict(age=query_results.iloc[i]['age'],
			gender=query_results.iloc[i]['gender'],
			ethnicity=query_results.iloc[i]['ethnicity'],
			priorDoctors=query_results.iloc[i]['priorDoctors'],
			waitYear=query_results.iloc[i]['waitYear'],
			medicationCount=query_results.iloc[i]['medicationCount'],
			costs=query_results.iloc[i]['costs']
			))

	features = [query_results.iloc[0]['priorDoctors'],
		query_results.iloc[0]['age'],
		query_results.iloc[0]['waitYear'],
		query_results.iloc[0]['reward'],
            	query_results.iloc[0]['medicationCount'],
		query_results.iloc[0]['costs']]

	y_true = query_results.iloc[i]['insight']
	#print(features)

	the_result = simpleModel.ModelIt(y_true,features)
	return render_template("output.html", features = query_list, the_result =the_result)

