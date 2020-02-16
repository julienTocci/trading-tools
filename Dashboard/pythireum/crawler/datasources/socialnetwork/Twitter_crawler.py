import tweepy
from tweepy.streaming import StreamListener
import json
# AWS credentials are retrieved from the file at the path: AWS_SHARED_CREDENTIALS_FILE
import boto3
import time
import sys
import threading


# relative path from where the TwitterCrawler is importer. To modify
creds = open('crawler/datasources/socialnetwork/creds.json', 'r')
creds_string = json.load(creds)

consumer_key = creds_string['consumer_key']
consumer_secret = creds_string['consumer_secret']
access_token = creds_string['access_token']
access_token_secret = creds_string['access_token_secret']


class MyStreamListener(tweepy.StreamListener):
    def __init__(self, boto_client, stream_name, crawler_instance):
        super(MyStreamListener, self).__init__()
        self.kinesis = boto_client
        self.stream_name = stream_name
        self.crawler_instance = crawler_instance

    def on_status(self, status):
        if (self.crawler_instance.status != "running"):
            return False
        print(status.txt)

    def on_data(self, data):
        if (self.crawler_instance.status != "running"):
            return False
        try:
            all_data = json.loads(data)
            tw_data = {}
            print("Collecting Tweet")

            #if 'lang' in all_data and (all_data['lang'] == "en"):
            # Didn't parse EVERYTHING (see example-tweet.json)
            tw_data['status_created_at']                = str(all_data["created_at"])
            tw_data['source']                           = str(all_data['source'])
            tw_data['text']                             = str(all_data['text'].encode('ascii', 'ignore').decode('ascii'))
            tw_data['user_id']                          = str(all_data['user']['id'])
            tw_data['user_name']                        = str(all_data['user']['name'])
            tw_data['user_location']                    = str(all_data['user']['location'])

            try:
                print("Sending Tweet data to stream: " + self.stream_name)
                ## Be carefull the Buffer conditions is 5 MB or 300 seconds before pushing to S3
                self.kinesis.put_record(DeliveryStreamName=self.stream_name,
                                        Record={'Data': json.dumps(tw_data) + ',\n'})
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

class TwitterCrawler(threading.Thread):
    # keywords = List
    # follow_list = List
    def __init__(self, threadID, keywords, follow_list):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.keywords = keywords
        self.follow_list = follow_list
        self.status = "created"

    def create_stream(self,client, stream_name):
        return client.create_delivery_stream(
            DeliveryStreamName=stream_name,
            S3DestinationConfiguration={
                'RoleARN': 'arn:aws:iam::896256228786:role/firehose_delivery_role',
                'BucketARN': 'arn:aws:s3:::kinesistwitterstream',
                'Prefix': stream_name + '//'
            }
        )

    def delete_stream(self, client, stream_name):
        try:
            print('Successfully delete kinesis stream: {}'.format(stream_name))
            return client.delete_delivery_stream(DeliveryStreamName=stream_name)
        except:
            print('Kinesis {} does not exist'.format(stream_name))


    def run(self):
        print ("Starting TwitterCrawler with ID:" + str(self.threadID) + ", for keywords: "+', '.join(self.keywords))
        self.status = "running"
        client = boto3.client('firehose', region_name='us-east-1')
        stream_name = '-'.join(self.keywords)+ "-twitter-" + str(self.threadID)
        try:
            self.create_stream(client, stream_name)
            print('Creating Twitter Kinesis stream... Please wait...')
            time.sleep(60)
        except:
            print("Failed to create Stream")
            pass
        stream_status = client.describe_delivery_stream(DeliveryStreamName=stream_name)
        if stream_status['DeliveryStreamDescription']['DeliveryStreamStatus'] == 'ACTIVE':
            print("\n ==== KINESES " + stream_name + " ONLINE ====")
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        streamListener = MyStreamListener(client, stream_name, self)
        stream = tweepy.Stream(auth=api.auth, listener=streamListener)

        print('Starting streaming '+ stream_name)
        while True:
            if self.status != "running":
                # We will be able to manage pausing the thread here
                print("Got stop signal for Twitter crawler " + stream_name)
                self.delete_stream(client, stream_name)
                break
            try:
                stream.filter(follow=self.follow_list)
                #stream.filter(follow=["1094299419556626432"])
            except:
                time.sleep(5)
                print('Sleeping 5 sec before next filter')
                pass

