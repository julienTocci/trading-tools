THis repo contains the main Pythireum Django (Python) web app which permits to start verifying data from 
multiple sources


## Install on ubuntu ##
## Use python3.7

sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt install python3.7
sudo apt-get purge libappstream3
sudo apt-get update

wget https://bootstrap.pypa.io/get-pip.py

ln -s python3.7 python

python get-pip.py

Following are useful for pattern-recog

python -m pip install numpy

python -m pip install matplotlib

sudo apt-get install python3.7-dev

sudo python -m pip uninstall lxml

sudo python -m pip install lxml


python -m pip install Django boto3 tweepy uuid django-bootstrap4 beautifulsoup4 scrapy crochet spacy textacy


python -m spacy download en_core_web_md

python -m spacy download fr_core_news_md

The following will downgrade spacy and make unavailable some models and function but allow to have entity number fro french text

## The best scenario would be to train our proper model for french texts ##

pip install https://github.com/pagesjaunes/spacy-french-models/releases/download/v0.0.1-alpha/fr_model-0.0.1.tar.gz

python -m spacy link fr_model fr_default --force



mkdir ~/.aws/
(For windows Change AWS_SHARED_CREDENTIALS_FILE  to the path of the file, put it wherever you want)
nano ~/.aws/credentials
		[default]
		aws_access_key_id=XXXX
		aws_secret_access_key=XXXXX


Create Kinesis delivery role (create kiensis firehose manually until it ask to create role)

Create S3 Bucket kinesistwitterstream
Create S3 Bucket kinesiscustomstream

Attach s3 admin policy to Kinesis role in AWS

Create twitter developper account, create a default app with randum url and get keys
Create a file creds.json in pythireum/crawler/datasources/socialnetwork/
 {
 	"consumer_key": "",
	"consumer_secret" : "",
	"access_token" : "",
	"access_token_secret" : "",
 }


## Starting the App ##
go in pythireum dir

python manage.py runserver 0.0.0.0:8000

## Admin interface ##

user = blocksnatchAdmin

pw = blockSnatch24!






TODO:

Think more about a meaningfull output
Maybe do not use NLP (too complex for now) but just package data and create summary documents


Twitter:  Add a lot more twitterID to follow and make it possible to specify them when creating a search with Twitter


custom: Create a one page document containing the body of each article concerning an index, specify the target url at creation


















