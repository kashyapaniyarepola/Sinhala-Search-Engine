from elasticsearch import Elasticsearch, helpers
import json



es = Elasticsearch([{'host': 'localhost', 'port':9200}])

def data_upload():
    with open('cricketers-corpus/si_cricketers.json', encoding="utf8") as f:
        data = json.loads(f.read())
    helpers.bulk(es, data, index='index-cricket', doc_type='srilankan-cricketers')


if __name__ == "__main__":
    data_upload()

