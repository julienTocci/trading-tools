import threading
import time


class LesObsParser(threading.Thread):
    def __init__(self, threadID, search_keywords, search_name, nlp_helper, s3_client):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.nlp_helper = nlp_helper
        self.s3_client = s3_client
        self.status = "created"

    def run(self):
        print ("Starting LesObsParser with ID:" + str(self.threadID))
        self.status = "running"

        while True:
            if self.status != "running":
                # We will be able to manage pausing the thread here
                print("Got stop signal for LesObs crawler"  + str(self.threadID))
                break
            try:
                time.sleep(2)
            except:
                pass