from elasticsearch import Elasticsearch, helpers
import json
from flask import Flask
from wtforms import Form, StringField, SelectField
from flask import flash, render_template, request, redirect, jsonify
import re
from googletrans import Translator
from search import search_query_filtered, search_query

es = Elasticsearch([{'host': 'localhost', 'port':9200}])
app = Flask(__name__)


global_search = "dada"
global_name = []
global_runs = []
global_wickets = []
global_teams = []
global_bio = []
global_career_info = []

@app.route('/', methods=['GET', 'POST'])
def index():
    global global_search
    global global_name
    global global_runs
    global global_wickets
    global global_teams
    global global_bio
    global global_career_info
    if request.method == 'POST':
        if 'form_1' in request.form:
            if request.form['nm']:
                search = request.form['nm']
                global_search = search
                print(global_search)
            else :
                search = global_search
            list_cricketers = search_query(search)
            # print (teams)
            # global_name, global_teams, global_bio, global_career_info = names, teams, bios, career_infos
        elif 'form_2' in request.form:
            search = global_search
            artist_filter = []
            genre_filter = []
            music_filter = []
            lyrics_filter = []
            for i in global_artists :
                if request.form.get(i["key"]):
                    artist_filter.append(i["key"])
            for i in global_genre :
                if request.form.get(i["key"]):
                    genre_filter.append(i["key"])
            for i in global_music:
                if request.form.get(i["key"]):
                    music_filter.append(i["key"])
            for i in global_lyrics:
                if request.form.get(i["key"]):
                    lyrics_filter.append(i["key"])
            list_cricketers, names, genres, music, lyrics = search_query_filtered(search, artist_filter, genre_filter, music_filter, lyrics_filter)
        
        return render_template('index.html', cricketers = list_cricketers)
    return render_template('index.html', cricketers = '')

if __name__ == "__main__":
    app.run(debug=True)
