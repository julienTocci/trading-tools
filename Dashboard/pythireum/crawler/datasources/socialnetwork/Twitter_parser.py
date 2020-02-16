import threading
import boto3
import json

class TwitterParser(threading.Thread):
    def __init__(self, threadID, search_keywords, search_instance, nlp_helper, s3_client):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.keywords = search_keywords
        self.search_instance = search_instance
        self.status = "created"
        self.nlp_helper = nlp_helper
        self.s3_client = s3_client

    def run(self):
        print ("Starting TwitterParser with ID:" + str(self.threadID))
        self.status = "running"

        # If there is only 1 keyword, we have to transform it as a list [theKeyword] in order for the
        # s3_prefix join not to separate the letter of the keyword (join is different between str and list)
        if isinstance(self.keywords, (list,)) == False:
            self.keywords = [self.keywords]


        ## TODO  ADD TRY CATCHS
        s3_prefix = '-'.join(self.keywords)+ "-twitter-" + str(self.threadID)
        response = self.s3_client.list_objects(Bucket='kinesistwitterstream', Prefix=s3_prefix)

        for content in response.get('Contents', []):
            obj = self.s3_client.get_object(Bucket='kinesistwitterstream', Key=content.get('Key'))
            j = obj['Body'].read().decode('utf-8')

            # Transforming single json object into an array of object
            j = "[" + j
            # Removing last trailing coma
            j = j[:-2]
            j = j + "]"

            tweets_json = json.loads(j)
            for tweet in tweets_json:
                self.nlp_helper.extract_entity_english(tweet["text"], self.search_instance.name, s3_prefix, tweet["status_created_at"])

        # We will have to adapt this to wait for all parser to finish before putting the boolean to true
        self.search_instance.parsing_in_progress = False
        self.search_instance.save()
