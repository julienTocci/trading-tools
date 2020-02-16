import threading
import time
import boto3
import json

class BoursiercomParser(threading.Thread):
    def __init__(self, threadID, search_keywords, search_instance, nlp_helper, s3_client):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.nlp_helper = nlp_helper
        self.search_instance = search_instance
        self.s3_client = s3_client
        self.status = "created"

    def run(self):
        print ("Starting BoursiercomParser with ID:" + str(self.threadID))
        self.status = "running"

        s3_prefix = "custom-boursiercom-" + str(self.threadID)
        response = self.s3_client.list_objects(Bucket='kinesiscustomstream', Prefix=s3_prefix)

        # Be carefull, it parses all file found = > parse X times the same data
        for content in response.get('Contents', []):
            obj = self.s3_client.get_object(Bucket='kinesiscustomstream', Key=content.get('Key'))
            j = obj['Body'].read().decode('utf-8')

            # Transforming single json object into an array of object
            j = "[" + j
            # Removing last trailing coma
            j = j[:-2]
            j = j + "]"

            last_parse_json = json.loads(j)

            for actuality in last_parse_json[0]["actualities"]:
                print(actuality["title"])
                self.nlp_helper.extract_entity_french(actuality["body"], self.search_instance.name, s3_prefix)

        print("Finished BoursiercomParser with ID:" + str(self.threadID))

        # We will have to adapt this to wait for all parser to finish before putting the boolean to true
        self.search_instance.parsing_in_progress = False
        self.search_instance.save()