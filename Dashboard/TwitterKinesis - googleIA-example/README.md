This tool permits to retrieve all tweets from a Twitter profile and apply NLP on it.


This is an example of the usage of the google sentiment analysis


Setup:
	- python -m pip install google-cloud
	- export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)"
	- echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
	- curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
	- sudo apt-get update && sudo apt-get install google-cloud-sdk
	- sudo apt install google-cloud-sdk-app-engine-python
	- gcloud init (and follow instructions)
	- sudo pip3 install google-cloud-language
	- sudo pip3 install --upgrade oauth2client
	- gcloud iam service-accounts create agregator
	- gcloud projects add-iam-policy-binding PROJECTID --member "serviceAccount:agregator@PROJECTID.iam.gserviceaccount.com" --role "roles/owner"
	- gcloud iam service-accounts keys create [FILE_NAME].json --iam-account [NAME]@[PROJECT_ID].iam.gserviceaccount.com
	-  export GOOGLE_APPLICATION_CREDENTIALS=~/google-creds.json




Go to google cloud console, AutoMl Natural Language and enable the API


Now everything is setup:
	You can create a Kinesis stream to follow some users and track only specific terms :
	  python3 createdatasource.py testKinesis

Get user Id you want to follow and put it in stream.filter(follow=)
https://tweeterid.com/

See patterns of track :
https://developer.twitter.com/en/docs/tweets/rules-and-filtering/overview/standard-operators.html

More information
https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters


Tests (https://developer.twitter.com/en/docs/tweets/filter-realtime/guides/basic-stream-parameters
):
- Putting track and followed show all tweet from anyone which contains track (doesn't seems to take into account follow)
- Putting only follow=['UserId'] permits to follow twitter from users (will get all tweets from the users?)