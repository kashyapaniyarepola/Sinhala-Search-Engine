from elasticsearch import Elasticsearch, helpers
import json
import re
from googletrans import Translator
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

es = Elasticsearch([{'host': 'localhost', 'port':9200}])


def post_processing_text(results):
    list_cricketers = []
    for i in range(len(results['hits']['hits'])) :
        bios = json.dumps(results['hits']['hits'][i]['_source']["bio"], ensure_ascii=False)
        bios = bios.replace('"', '')
        bios = bios.replace("'", '')       
        bios = bios.replace('\\', '')
        bios = bios.replace('t', '')
        bios = bios.replace('\xa0', '')
        bios = "<br>".join(bios.split("n"))
        bios =  re.sub(r'(<br> )+', r'\1', bios)
        j = 0
        while True :
            if bios[j] == '<' or bios[j] == '>' or bios[j] == 'b' or bios[j] == 'r' or bios[j] == ' ':
                j += 1
            else :
                break
        bios = bios[j:]
        results['hits']['hits'][i]['_source']["bio"] = bios
        list_cricketers.append(results['hits']['hits'][i]['_source'])
    aggregations = results['aggregations']
    ball_ranks = aggregations['ball_rank']['buckets']
    bat_ranks = aggregations['bat_rank']['buckets']
    teams = aggregations['teams']['buckets']
    wickets = aggregations['wickets']['buckets']
    runs = aggregations['runs']['buckets']
    bios = aggregations['bio']['buckets']
    gender = aggregations['gender']['buckets']
    career_infos = aggregations['career_info']['buckets']
    # print(aggregations)
    return list_cricketers, teams, gender 


def search_text(search_term):
    results = es.search(index='index-cricket',doc_type = 'srilankan-cricketers',body={
        "size" : 500,
        "query" :{
            "multi_match": {
                "query" : search_term,
                "type" : "best_fields",
                "fields" : [
                    "name", "teams", "bio", 
                    "career_info", "gender",
                    "bat_rank","ball_rank","runs", "wickets"]
                    
            }
        },
        "aggs": {
            "wickets": {
                "terms": {
                    "field": "wickets.keyword",
                    "size" : 15    
                }        
            },
            "runs": {
                "terms": {
                    "field": "runs.keyword",
                    "size" : 15    
                }        
            },
            "gender": {
                "terms": {
                    "field": "gender.keyword",
                    "size" : 15    
                }        
            },
            "bat_rank": {
                "terms": {
                    "field": "bat_rank.keyword",
                    "size" : 15    
                }        
            },
            "ball_rank": {
                "terms": {
                    "field": "ball_rank.keyword",
                    "size" : 15    
                }        
            },
            "teams": {
                "terms": {
                    "field":"teams.keyword",
                    "size" : 15
                }             
            },
            "career_info": {
                "terms": {
                    "field":"career_info.keyword",
                    "size" : 15
                }             
            },
            "bio": {
                "terms": {
                    "field":"bio.keyword",
                    "size" : 15
                }             
            },

        }

    })

    # print(results)
    list_cricketers, teams, gender =  post_processing_text(results)
    return list_cricketers, teams, gender

def search_query_classifier(search_term):
    classifier = False
    gender_filter = [] 
    teams_filter = []

    gender_keys = ["කාන්තා", "ක්‍රීඩිකාවෝ", "කාන්තාව", "ක්‍රීඩිකාව", "ක්‍රීඩිකාවන්"]
    teams_keys = ["කණ්ඩායම", "සමාජය", "කණ්ඩායම්", "වෙනුවෙන්", "කණ්ඩායමට"]
    search_term_list = search_term.split()

    for j in search_term_list:
        if j in gender_keys:
            gender_filter.append("කාන්තා")
            classifier = True
        if j in teams_keys:
            # search_term_list.pop(j)
            teams_filter.append(search_term)
            classifier = True

    return classifier, gender_filter, teams_filter

def search_filter_text(search_term, gender_filter, teams_filter):
    must_list = [{
                    "multi_match": {
                        "query" : search_term,
                        "type" : "best_fields",
                        "fields" : [
                            "name", "teams", "bio", 
                            "career_info", "gender",
                            "bat_rank","ball_rank","runs", "wickets"]
                            
                    }
                }]
    if len(gender_filter) != 0 :
        must_list.append({"match" : {"gender": gender_filter[0]}})
    if len(teams_filter) != 0 :
        must_list.append({"match" : {"teams": teams_filter[0]}})
   
    results = es.search(index='index-cricket',doc_type = 'srilankan-cricketers',body={
        "size" : 500,
        "query" :{
            "bool": {
                "must": must_list
            }
        },
        "aggs": {
            "wickets": {
                "terms": {
                    "field": "wickets.keyword",
                    "size" : 15    
                }        
            },
            "runs": {
                "terms": {
                    "field": "runs.keyword",
                    "size" : 15    
                }        
            },
            "gender": {
                "terms": {
                    "field": "gender.keyword",
                    "size" : 15    
                }        
            },
            "bat_rank": {
                "terms": {
                    "field": "bat_rank.keyword",
                    "size" : 15    
                }        
            },
            "ball_rank": {
                "terms": {
                    "field": "ball_rank.keyword",
                    "size" : 15    
                }        
            },
            "teams": {
                "terms": {
                    "field":"teams.keyword",
                    "size" : 15
                }             
            },
            "career_info": {
                "terms": {
                    "field":"career_info.keyword",
                    "size" : 15
                }             
            },
            "bio": {
                "terms": {
                    "field":"bio.keyword",
                    "size" : 15
                }             
            },
        }
    })
    list_cricketers, teams, gender =  post_processing_text(results)
    return list_cricketers, teams, gender


def search_query(search_term):
    classifier, gender_filter, teams_filter = search_query_classifier(search_term)  
    if classifier :
        list_cricketers, teams, gender = search_filter_text(search_term,gender_filter, teams_filter)
    else :
        list_cricketers, teams, gender = search_text(search_term)

    return list_cricketers, teams, gender

    
    
            







    
