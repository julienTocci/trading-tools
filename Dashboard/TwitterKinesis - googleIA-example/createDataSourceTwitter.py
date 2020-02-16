import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import json
import boto3
import uuid
import time
import sys
#from oauth2client.client import GoogleCredentials
#google_credentials = GoogleCredentials.get_application_default()

#Twitter Keys

creds = open('creds.json', 'r')
creds_string = json.load(creds)

consumer_key = creds_string['consumer_key']
consumer_secret = creds_string['consumer_secret']
access_token = creds_string['access_token']
access_token_secret = creds_string['access_token_secret']

def sentimentAnalysis(text):
    print("Starting sentiment Analysis")
    client = language.LanguageServiceClient()
    print("Creating document")
    document = types.Document(content=text,type=enums.Document.Type.PLAIN_TEXT)
    print("Analysing sentiments")
    sent_analysis = client.analyze_sentiment(document=document)
    print_result_analysis(sent_analysis)
    return sent_analysis

def print_result_analysis(annotations):
    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    for index, sentence in enumerate(annotations.sentences):
        sentence_sentiment = sentence.sentiment.score
        print('Sentence {} has a sentiment score of {}'.format(
            index, sentence_sentiment))

    print('Overall Sentiment: score of {} with magnitude of {}'.format(
        score, magnitude))
    return 0


def create_stream(client, stream_name):
    return client.create_delivery_stream(
        DeliveryStreamName=stream_name ,
        S3DestinationConfiguration={
        'RoleARN': 'arn:aws:iam::896256228786:role/firehose_delivery_role',
        'BucketARN': 'arn:aws:s3:::kinesistwitterstream',
        'Prefix': stream_name+'//'
    }
    )

class StreamListener(tweepy.StreamListener):
    def __init__(self, boto_client, search_list):
        super(tweepy.StreamListener, self).__init__()
        self.kinesis = boto_client
        self.search_list = search_list

    def on_status(self, status):
        print(status.txt)

    def on_data(self, data):
        try:
            all_data = json.loads(data)
            print("DATA: ", all_data)
            tw_data = {}
            status_sent_entity = {}
            retweet_status_sent_entity = {}
            print("Collecting Tweet")

            if 'lang' in all_data and (all_data['lang'] == "en"):
                print("Enter if")
                # Didn't parse EVERYTHING (see example-tweet.json)
                tw_data['status_created_at']                = str(all_data["created_at"])
                tw_data['status_id']                        = str(all_data["id"])
                tw_data['source']                           = str(all_data['source'])
                tw_data['text']                             = str(all_data['text'].encode('ascii', 'ignore').decode('ascii'))
                tw_data['truncated']                        = str(all_data['truncated'])
                tw_data['in_reply_to_status_id']            = str(all_data['in_reply_to_status_id'])
                tw_data['in_reply_to_user_id']              = str(all_data['in_reply_to_user_id'])
                tw_data['in_reply_to_screen_name']          = str(all_data['in_reply_to_screen_name'])
                tw_data['user_id']                          = str(all_data['user']['id'])
                tw_data['user_name']                        = str(all_data['user']['name'])
                tw_data['user_location']                    = str(all_data['user']['location'])
                tw_data['user_friend_count']                = str(all_data['user']['friends_count'])
                tw_data['user_follower_count']              = str(all_data['user']['followers_count'])
                tw_data['user_statuses_count']              = str(all_data['user']['statuses_count'])
                tw_data['user_following_count']    = str(all_data['user']['following'])
                try:
                    print("Enter try 1")
                    analysis                          = sentimentAnalysis(tw_data['text'])
                    tw_data['status_sentimentScore']              = analysis.document_sentiment.score
                    tw_data['status_stentimentMagnitude']         = analysis.document_sentiment.magnitude
                except:
                    tw_data['status_sentimentScore']              = 'None'

                try:
                    print("Enter try 2")
                    self.kinesis.put_record(DeliveryStreamName=self.search_list[0],
                                            Record={'Data': json.dumps(tw_data) + '\n'})
                    print("Finished put record")
                    pass

                except Exception as e:
                    print("Failed Kinesis Put Record {}".format(str(e)))

        except BaseException as e:
            print("failed on data ", str(e))
            time.sleep(5)

    def on_error(self, status_code):
        if status_code == 420:
            print('Received status code 420')
            return False


def main(search_list):
    stream_name = search_list[0]
    client = boto3.client('firehose', region_name='us-east-1')
    try:
        create_stream(client,stream_name)
        print('Creating Kinesis stream... Please wait...')
        time.sleep(60)
    except:
        print("Failed to create Stream")
        pass
    stream_status = client.describe_delivery_stream(DeliveryStreamName=stream_name)
    if stream_status['DeliveryStreamDescription']['DeliveryStreamStatus'] == 'ACTIVE':
        print("\n ==== KINESES ONLINE ====")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    streamListener = StreamListener(client, search_list)
    stream = tweepy.Stream(auth=api.auth, listener=streamListener)
    
    print('Starting streaming')
    while True:
        try:
            stream.filter(follow=["1094299419556626432"])
        except:
            time.sleep(5)
            print('Sleeping 5 sec before next filter')
            pass


if __name__ == '__main__':
    main(sys.argv[1:])