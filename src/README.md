## How to Run. 
To install required dependencies
```
conda create -n treesequences python=3.10
conda activate treesequences
pip install -r requirments.txt
```

### Run elastic-search server [link](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
after installing: 
in the `config/elasticsearch.yml` file - change the following values

```
http.port: 9200

xpack.security.enabled: false

xpack.security.enrollment.enabled: false

xpack.security.http.ssl:
  enabled: false
  keystore.path: certs/http.p12

xpack.security.transport.ssl:
  enabled: false
```


create a folder "src/data" and download this file using this [link](https://drive.google.com/file/d/1pkV2PRwefiteQRreSd7DZsgkdyrmo1Wq/view?usp=drive_link)

To test the program, run the following command:
```
python langgraph_tskit.py
```
