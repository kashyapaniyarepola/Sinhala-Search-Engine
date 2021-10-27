from elasticsearch import Elasticsearch, helpers
import json
import re
from googletrans import Translator
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

es = Elasticsearch([{'host': 'localhost', 'port':9200}])

def translate_to_english(value):
	translator = Translator()
	#english_term = translator.translate(value, dest='en')
	return value

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
    teams = aggregations['teams']['buckets']['key']
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

# def search_filter_text(search_term, artist_filter, genre_filter, music_filter, lyrics_filter):
#     must_list = [{
#                     "multi_match": {
#                         "query" : search_term,
#                         "type" : "best_fields",
#                         "fields" : [
#                             "title", "Artist_si", "Artist_en","Genre_si","Genre_en", 
#                             "Lyrics_si", "Lyrics_en","Music_si","Music_en", "song_lyrics"]
                            
#                     }
#                 }]
#     if len(artist_filter) != 0 :
#         for i in artist_filter :
#             must_list.append({"match" : {"Artist_si": i}})
#     if len(genre_filter) != 0 :
#         for i in genre_filter :
#             must_list.append({"match" : {"Genre_si": i}})
#     if len(music_filter) != 0 :
#         for i in music_filter :
#             must_list.append({"match" : {"Music_si": i}})
#     if len(lyrics_filter) != 0 :
#         for i in lyrics_filter :
#             must_list.append({"match" : {"Lyrics_si": i}})
#     results = es.search(index='index-songs',doc_type = 'sinhala-songs',body={
#         "size" : 500,
#         "query" :{
#             "bool": {
#                 "must": must_list
#             }
#         },
#         "aggs": {
#             "genre": {
#                 "terms": {
#                     "field": "Genre_si.keyword",
#                     "size" : 15    
#                 }        
#             },
#             "artist": {
#                 "terms": {
#                     "field":"Artist_si.keyword",
#                     "size" : 15
#                 }             
#             },
#             "music": {
#                 "terms": {
#                     "field":"Music_si.keyword",
#                     "size" : 15
#                 }             
#             },
#             "lyrics": {
#                 "terms": {
#                     "field":"Lyrics_si.keyword",
#                     "size" : 15
#                 }             
#             },

#         }
#     })
#     list_songs, artists, genres, music, lyrics = post_processing_text(results)
#     return list_songs, artists, genres, music, lyrics





def intent_classifier(search_term):

    select_type = False
    resultword = ''

    keyword_top = ["top", "best", "popular", "good", "great"]
    keyword_song = ["song", "sing", "sang", "songs", "sings"]
    search_term_list = search_term.split()
    for j in search_term_list : 
        documents = [j]
        documents.extend(keyword_top)
        documents.extend(keyword_song)
        tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
        tfidf_matrix = tfidf_vectorizer.fit_transform(documents)

        cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)
        similarity_list = cs[0][1:]

        for i in similarity_list :
            if i > 0.8 :
                select_type  = True
    if select_type :
        querywords = search_term.split()
        querywords  = [word for word in querywords if word.lower() not in keyword_top]
        querywords  = [word for word in querywords if word.lower() not in keyword_song]
        resultword = ' '.join(querywords)

    
    return select_type,  resultword


def top_most_text(search_term):

    with open('song-corpus/songs_meta_all.json') as f:
        meta_data = json.loads(f.read())

    artist_list = meta_data["Artist_en"]
    genre_list = meta_data["Genre_en"]
    music_list = meta_data["Music_en"]
    lyrics_list = meta_data["Lyrics_en"]

    documents_artist = [search_term]
    documents_artist.extend(artist_list)
    documents_genre = [search_term]
    documents_genre.extend(genre_list)
    documents_music = [search_term]
    documents_music.extend(music_list)
    documents_lyrics = [search_term]
    documents_lyrics.extend(lyrics_list)
    query = []
    select_type = False

    size = 100
    term_list = search_term.split()
    print(term_list)
    for i in term_list:
        if i.isnumeric():
            size = int(i)

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_artist)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]

    max_val = max(similarity_list)
    other_select = False
    if max_val >  0.85 :
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"Artist_en": artist_list[i]}})
        select_type = True
        other_select = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_genre)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]

    max_val = max(similarity_list)
    if max_val >  0.85 :
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"Genre_en": genre_list[i]}})
        select_type = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_music)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]
    max_val = max(similarity_list)
    if max_val >  0.85 and other_select == False:
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"Music_en": music_list[i]}})
        select_type = True
        other_select = True

    tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
    tfidf_matrix = tfidf_vectorizer.fit_transform(documents_lyrics)

    cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

    similarity_list = cs[0][1:]
    max_val = max(similarity_list)
    if max_val >  0.85 and other_select == False:
        loc = np.where(similarity_list==max_val)
        i = loc[0][0]
        query.append({"match" : {"Lyrics_en": lyrics_list[i]}})
        select_type = True
        other_select = True
    
    if select_type != True :
        query.append({"match_all" : {}})

    print(query)
    results = es.search(index='index-songs',doc_type = 'sinhala-songs',body={
        "size" : size,
        "query" :{
            "bool": {
                "must": query
            }
        },
        "sort" :{
            "views": {"order": "desc"}
        },
        "aggs": {
            "genre": {
                "terms": {
                    "field": "Genre_si.keyword",
                    "size" : 15    
                }        
            },
            "artist": {
                "terms": {
                    "field":"Artist_si.keyword",
                    "size" : 15
                }             
            },
            "music": {
                "terms": {
                    "field":"Music_si.keyword",
                    "size" : 15
                }             
            },
            "lyrics": {
                "terms": {
                    "field":"Lyrics_si.keyword",
                    "size" : 15
                }             
            },

        }
    })
    list_songs, artists, genres, music, lyrics = post_processing_text(results)
    return list_songs, artists, genres, music, lyrics

# def top_most_filter_text(search_term, artist_filter, genre_filter, music_filter, lyrics_filter):

#     with open('song-corpus/songs_meta_all.json') as f:
#         meta_data = json.loads(f.read())

#     artist_list = meta_data["Artist_en"]
#     genre_list = meta_data["Genre_en"]
#     music_list = meta_data["Music_en"]
#     lyrics_list = meta_data["Lyrics_en"]

#     documents_artist = [search_term]
#     documents_artist.extend(artist_list)
#     documents_genre = [search_term]
#     documents_genre.extend(genre_list)
#     documents_music = [search_term]
#     documents_music.extend(music_list)
#     documents_lyrics = [search_term]
#     documents_lyrics.extend(lyrics_list)
#     query = []
#     select_type = False
#     size = 100
#     term_list = search_term.split()
#     for i in term_list:
#         if i.isnumeric():
#             size = i

#     if len(artist_filter) != 0 :
#         for i in artist_filter :
#             query.append({"match" : {"Artist_si": i}})
#     if len(genre_filter) != 0 :
#         for i in genre_filter :
#             query.append({"match" : {"Genre_si": i}})
#     if len(music_filter) != 0 :
#         for i in music_filter :
#             query.append({"match" : {"Music_si": i}})
#     if len(lyrics_filter) != 0 :
#         for i in lyrics_filter :
#             query.append({"match" : {"Lyrics_si": i}})


#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_artist)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]
#     other_select = False
#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False:
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Artist_en": artist_list[i]}})
#         select_type = True
#         other_select = True

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_genre)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]

#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False:
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Genre_en": genre_list[i]}})
#         select_type = True

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_music)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]
#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False:
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Music_en": music_list[i]}})
#         select_type = True
#         other_select = True

#     tfidf_vectorizer = TfidfVectorizer(analyzer="char", token_pattern=u'(?u)\\b\w+\\b')
#     tfidf_matrix = tfidf_vectorizer.fit_transform(documents_lyrics)

#     cs = cosine_similarity(tfidf_matrix[0:1],tfidf_matrix)

#     similarity_list = cs[0][1:]
#     max_val = max(similarity_list)
#     if max_val >  0.85 and other_select == False :
#         loc = np.where(similarity_list==max_val)
#         i = loc[0][0]
#         query.append({"match" : {"Lyrics_en": lyrics_list[i]}})
#         select_type = True
#         other_select = True
    
#     if select_type != True :
#         query.append({"match_all" : {}})

#     print(query)
#     results = es.search(index='index-songs',doc_type = 'sinhala-songs',body={
#         "size" : 500,
#         "query" :{
#             "bool": {
#                 "must": query
#             }
#         },
#         "sort" :{
#             "views": {"order": "desc"}
#         },
#         "aggs": {
#             "genre": {
#                 "terms": {
#                     "field": "Genre_si.keyword",
#                     "size" : 15    
#                 }        
#             },
#             "artist": {
#                 "terms": {
#                     "field":"Artist_si.keyword",
#                     "size" : 15
#                 }             
#             },
#             "music": {
#                 "terms": {
#                     "field":"Music_si.keyword",
#                     "size" : 15
#                 }             
#             },
#             "lyrics": {
#                 "terms": {
#                     "field":"Lyrics_si.keyword",
#                     "size" : 15
#                 }             
#             },

#         }
#     })
#     list_songs, artists, genres, music, lyrics = post_processing_text(results)
#     return list_songs, artists, genres, music, lyrics


def search_query(search_term):
    english_term = translate_to_english(search_term)
    select_type, strip_term = intent_classifier(english_term)  
    if select_type :
        list_songs, artists, genres, music, lyrics = top_most_text(strip_term)
    else :
        list_cricketers, teams, gender = search_text(search_term)

    return list_cricketers, teams, gender


# def search_query_filtered(search_term, artist_filter, genre_filter, music_filter, lyrics_filter):
#     english_term = translate_to_english(search_term)
#     select_type, strip_term = intent_classifier(english_term)  
#     if select_type :
#         list_songs, artists, genres, music, lyrics = top_most_filter_text(strip_term, artist_filter, genre_filter, music_filter, lyrics_filter)
#     else :
#         list_songs, artists, genres, music, lyrics = search_filter_text(search_term, artist_filter, genre_filter, music_filter, lyrics_filter)

#     return list_songs, artists, genres, music, lyrics
    
    
            







    
