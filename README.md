# Sinhala-Search-Engine
This repository conatins simple Sinhala search engine for Sri Lankan cricketers. This project is developed as a IR project CS4642 Data Mining and Information Retrieval

## Getting Started
You can install elasticsearch locally or otherwise, [visit](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
- Download & Extract the zip file
- Open ***cmd*** & Navigate to bin folder
- Start elasticsearch
```
[path-to-elasticsearch]\elasticsearch-x.x.x\bin> elasticsearch
```
This will create an elacticsearch cluster on port 9200. You can check the server by browsing http://localhost:9200.
```
{
  "name" : "Kashyapa Niyarepola",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "PcJXiFECQraR-G2wFugtOg",
  "version" : {
    "number" : "7.15.1",
    "build_flavor" : "default",
    "build_type" : "zip",
    "build_hash" : "83c34f456ae29d60e94d886e455e6a3409bba9ed",
    "build_date" : "2021-10-07T21:56:19.031608185Z",
    "build_snapshot" : false,
    "lucene_version" : "8.9.0",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```
- Clone the repository
```
git clone https://github.com/kashyapaniyarepola/Sinhala-Search-Engine.git
```
- Navigate to the project directory
- Install Virtualenv
```
[path-to-project]\Sinhala-Search-Engine> pip3 install virtualenv
```
- Create a virtual environment
```
[path-to-project]\Sinhala-Search-Engine> virtualenv virtualenv_name
```
- Activate created virtual environment
```
[path-to-project]\Sinhala-Search-Engine\virtualenv_name\Scripts> activate
```
- Install required libraries
```
[path-to-project]\Sinhala-Search-Engine> pip3 install -r requirements.txt
```
- Upload the data to elascticsearch cluster
```
[path-to-project]\Sinhala-Search-Engine> python data_upload.py
```
You can ckeck uploaded data are on the cluster by browsing http://localhost:9200/index-cricket/srilankan-cricketers/_search.
- Start the Flask app
```
[path-to-project]\Sinhala-Search-Engine> python app.py
```
You are done! You can search Sri Lankan creicketers by opening http://localhost:5000/. Happy Searching!

## Directory Structure
| Directory | Description |
| --- | --- |
| cricketers-corpus | Contain final dataset of Sri Lankan cricketers |
| templates | UI files |
| app.py | Flask app |
| data_upload.py | File for uploading data to elasticsearch cluster |
| search.py | Search functions for elasticsearch queries |
| search_queries.txt | Sample search queries |

## Data Fields
| Filed | Example |
| --- | --- |
| Name | චමරි අතපත්තු |
| Gender | කාන්තා |
| Runs | එක් දින ජාත්‍යන්තර තරඟ 84 ලකුණු 2625, විස්සයි විස්ස තරග 85 ලකුණු 1646 |
| Wickets | එක් දින ජාත්‍යන්තර තරඟ 84 කඩුලු 23, විස්සයි විස්ස 85 තරග කඩුලු 26 |
| Balling Rank | එක් දින ජාත්‍යන්තර පන්දු යැවීමේ ස්ථානය 62, විස්සයි විස්ස පන්දු යැවීමේ ස්ථානය 56 |
| Batting Rank | එක් දින ජාත්‍යන්තර පිතිකරණ ස්ථානය 16, විස්සයි විස්ස පිතිකරණ ස්ථානය 14 |
| Bio | අතපත්තු මුදියන්සේලාගේ චමරි ජයංගනී (උපත 1990 පෙබරවාරි 9, චමරි අතපත්තු ලෙසද හැඳින්වේ) යනු more... |
| Teams |ශ්‍රී ලංකාව, මෙල්බර්න් රෙනේගේඩ්ස්, යෝක්ෂයර් දියමන්ති, more... |
| Career Info | ඇය ඉහළ පෙළේ ආක්‍රමණශීලී පිතිකරණය සඳහා ප්‍රසිද්ධය. 2013 කාන්තා ක්‍රිකට් ලෝක කුසලානයේදී more... |

## Indexing and Quering

## Features
