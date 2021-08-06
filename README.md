# Solr  Re-Indexer
* A simple Python script to re-index a content collection from one Solr server to another.

## Prerequisite
You need to have Python package management tools [pip](https://pip.pypa.io/en/stable/) and [pipenv](https://docs.pipenv.org/) installed on your machine. 

## Usage
```
python3 solr-re-indexer.py -s <source server> -t <target server> -c <Solr collection> -u <Solr username> -p <Solr password> -b <batch size>
```

#### Sample run
* Source server: server1.ying.com:7001
* Target server: server2.ying.com:8983
* Collection name: test
* Solr username: xxx
* Solr password: xxx
```
$ pipenv install
Installing dependencies from Pipfile.lock (1b2c5a)...
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 0/0 — 00:00:00
To activate this project's virtualenv, run pipenv shell.
Alternatively, run a command inside the virtualenv with pipenv run.
$ pipenv shell  
Launching subshell in virtual environment...
 . /Users/ying/.local/share/virtualenvs/solr-re-indexer-Q324kecP/bin/activate
 %  . /Users/ying/.local/share/virtualenvs/solr-re-indexer-Q324kecP/bin/activate
solr-re-indexer % python3 solr-re-indexer.py -s server1.ying.com:7001 -t server2.ying.com:8983 -c test -u xxx -p xxx -b 10
Do we need to use HTTPS for server1.ying.com:7001? (Y/N) Y
Do we need to use HTTPS for server2.ying.com:8983? (Y/N) Y
	Collection name:  test
	Total document count:  27
	Batch size: 10
	Number of batches: 3
Start solr-re-indexing...
Documents processed: 100%|██████████| 3/3 [00:01<00:00,  2.54it/s]
solr-re-indexer % 

```

## Warning
* It does not preserve any fields that are not stored, so you should not use this tool to re-index if your collection contains fields that are not stored. Instead, re-index from source data.
* It has some custom logic to remove any fields that starts with the underscore character(_). You may want to remove or modify this logic according to your data filtering needs.
* You may need to replace the dummy SSL/TLS certificate files (cert/source_server.crt, cert/ target_server.crt) with your real certificate files when using HTTPS connections.
