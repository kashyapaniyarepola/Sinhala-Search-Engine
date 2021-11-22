from elasticsearch import Elasticsearch, helpers
import json
import re
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
    teams = aggregations['teams']['buckets']
    gender = aggregations['gender']['buckets']
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
    rank_filter = []
    bat_rank_filter = []
    ball_rank_filter = []
    run_filter = []
    wicket_filter = []
    allrounder_filter =[]

    gender_keys = ["කාන්තා", "ක්‍රීඩිකාවෝ", "කාන්තාව", "ක්‍රීඩිකාව", "ක්‍රීඩිකාවන්"]
    teams_keys = ["කණ්ඩායම", "සමාජය", "කණ්ඩායම්", "වෙනුවෙන්", "කණ්ඩායමට"]
    rank_keys = ["විස්සයි","විස්ස", "එක්" ,"දින" ,"ජාත්‍යන්තර", "ටෙස්ට්"]
    search_term_list = search_term.split()

    for j in search_term_list:
        if j in gender_keys:
            gender_filter.append("කාන්තා")
            classifier = True
        if j in teams_keys:
            # search_term_list
            # new_search_term = ""
            # for k in search_term_list:
            #     if k==j:
            #         continue
            #     new_search_term += k
            teams_filter.append(search_term)
            classifier = True
        if j in rank_keys:
            if "වර්තමාන" in search_term_list:
                if "පිතිකරුවන්" in search_term_list:
                    bat_rank_filter.append(search_term)
                elif "යවන්නන්" in search_term_list:
                    ball_rank_filter.append(search_term)
                elif "ඉරියව්" in search_term_list:
                    rank_filter.append(search_term)
                else:
                    rank_filter.append(search_term)
            else:
                if "පිතිකරුවන්" in search_term_list:
                    run_filter.append(search_term)
                elif "යවන්නන්" in search_term_list:
                    wicket_filter.append(search_term)
                elif "ඉරියව්" in search_term_list:
                    allrounder_filter.append(search_term)
                else:
                    allrounder_filter.append(search_term)
            classifier = True

    return classifier, gender_filter, teams_filter, rank_filter,bat_rank_filter, ball_rank_filter, run_filter,wicket_filter, allrounder_filter

def search_filter_text(search_term, gender_filter, teams_filter, rank_filter,bat_rank_filter, ball_rank_filter, run_filter,wicket_filter, allrounder_filter):
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
    must_list =[]
    if len(gender_filter) != 0 :
        must_list.append({"match" : {"gender": gender_filter[0]}})
    if len(teams_filter) != 0 :
        must_list.append({"match" : {"teams": teams_filter[0]}})
    if len(rank_filter) != 0 :
        must_list.append({"match" : {"ball_rank": rank_filter[0]}})
        must_list.append({"match" : {"bat_rank": rank_filter[0]}})
    if len(bat_rank_filter) != 0 :
        must_list.append({"match" : {"bat_rank": bat_rank_filter[0]}})
    if len(ball_rank_filter) != 0 :
        must_list.append({"match" : {"ball_rank": ball_rank_filter[0]}})

    if len(allrounder_filter) != 0 :
        must_list.append({"match" : {"runs": allrounder_filter[0]}})
        must_list.append({"match" : {"wickets": allrounder_filter[0]}})
    if len(run_filter) != 0 :
        must_list.append({"match" : {"runs": run_filter[0]}})
    if len(wicket_filter) != 0 :
        must_list.append({"match" : {"wickets": wicket_filter[0]}})
   
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
    classifier, gender_filter, teams_filter, rank_filter,bat_rank_filter, ball_rank_filter, run_filter,wicket_filter, allrounder_filter = search_query_classifier(search_term)  
    if classifier :
        list_cricketers, teams, gender = search_filter_text(search_term,gender_filter, teams_filter, rank_filter,bat_rank_filter, ball_rank_filter, run_filter,wicket_filter, allrounder_filter)
    else :
        list_cricketers, teams, gender = search_text(search_term)

    return list_cricketers, teams, gender

    
    
            







    
