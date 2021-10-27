from elasticsearch import Elasticsearch, helpers
import json
from flask import Flask
from wtforms import Form, StringField, SelectField
from flask import flash, render_template, request, redirect, jsonify
import re
from googletrans import Translator
# from search import search_query_filtered, search_query
from search import search_query

es = Elasticsearch([{'host': 'localhost', 'port':9200}])
app = Flask(__name__)


global_search = "dada"
global_name = []
global_runs = []
global_wickets = []
global_teams = []
global_bio = []
global_gender = []
global_career_info = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global global_search
    global global_name
    global global_runs
    global global_wickets
    global global_teams
    global global_bio
    global global_gender
    global global_career_info
    if request.method == 'POST':
        if 'form_1' in request.form:
            if request.form['nm']:
                search = request.form['nm']
                global_search = search
                print(global_search)
            else :
                search = global_search
            list_cricketers, teams, gender = search_query(search)
            # print (teams)
            global_gender, global_teams  = teams, gender
        
        return render_template('index.html', cricketers = list_cricketers, teams = teams, gender = gender)
    return render_template('index.html', cricketers = '', teams ='', gender='')

if __name__ == "__main__":
    app.run(debug=True)
