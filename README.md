# Sinhala-Search-Engine
This repository conatins simple Sinhala search engine for Sri Lankan cricketers. This project is developed as a IR project CS4642 Data Mining and Information Retrieval

## Getting Started
You can install elasticsearch locally or otherwise, [visit](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
- Download & Extract the zip file
- Open ***cmd*** & Navigate to bin folder
- Start elasticsearch
```
[path-to-elasticsearch]/elasticsearch-x.x.x/bin> elasticsearch
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

```
```
- Start the elasticsearch cluster on port 9200
- John Adams
- Thomas Jefferson
```
## Directory Structure
| Directory | Description |
| --- | --- |
| cricketers-corpus | Contain final dataset of Sri Lankan cricketers |
| templates | UI files |
| app.py | Flask app |
| data_upload.py | File for uploading data to elasticsearch cluster |
| search.py | Search functions for elasticsearch queries |
| search_queries.txt | Sample search queries |

