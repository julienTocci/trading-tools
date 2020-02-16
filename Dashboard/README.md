THis repo contains the main Pythireum Django (Python) web app which permits to start verifying data from 
multiple sources


## Install on ubuntu ##
## Use python3.6

sudo -H apt-get install python3-pip
sudo pip3 install virtualenv 
virtualenv -p python3 scrapy

source scrapy/bin/activate
sudo pip3 install scrapy
pip install pypiwin32
sudo pip3 install crochet

sudo pip3 install boto3
sudo pip3 install tweepy
sudo pip3 install uuid
sudo pip3 install Django
pip install django-bootstrap4
pip install beautifulsoup4

Not used anymore pip install py-translate

install  Visual C++ Build Tools 2015
pip3 install -U spacy (if not working on windows: dl the correct (32bit vs 64 and py version)whl file on https://www.lfd.uci.edu/~gohlke/pythonlibs/#spacy and do pip install spacy.whl)
pip install textacy
python -m spacy download en_core_web_lg
python -m spacy download en_core_web_md
python -m spacy download fr_core_news_md

# The following will downgrade spacy and make unavailable some models and function but allow to have entity number fro french text
# The best scenario would be to train our proper model for french texts
pip install https://github.com/pagesjaunes/spacy-french-models/releases/download/v0.0.1-alpha/fr_model-0.0.1.tar.gz
AS ADMIN CMD   python -m spacy link fr_model fr_default --force

sudo pip3 install requests (OPTIONAL?)
sudo pip3 install urllib3 (OPTIONAL?)

mkdir ~/.aws/
(For windows Change AWS_SHARED_CREDENTIALS_FILE  to the path of the file, put it wherever you want)
nano ~/.aws/credentials
		[default]
		aws_access_key_id=XXXX
		aws_secret_access_key=XXXXX


Create Kinesis delivery role (create kiensis firehose manually until it ask to create role)
Create S3 Bucket kinesistwitterstream

Attach s3 admin policy to Kinesis role in AWS

Create twitter developper account, create a default app with randum url and get keys
Create a file creds.json
 {
 	"consumer_key": "",
	"consumer_secret" : "",
	"access_token" : "",
	"access_token_secret" : "",
 }



## Starting the App ##
python manage.py runserver (the server will run on localhost:8000)

## Admin interface ##
user = blocksnatchAdmin
pw = blockSnatch24!