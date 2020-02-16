import threading
import time

class LesObsCrawler(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.status = "created"

    def run(self):
        print ("Starting LesObsCrawler with ID:" + str(self.threadID))
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