import threading
import time
import scrapy
from scrapy.settings import Settings
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor
from ..spider.boursiercom_spider import BoursierCom
import boto3

from crochet import setup
setup()


class BoursiercomCrawler(threading.Thread):
    def __init__(self, threadID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.status = "created"


    def run(self):
        print("Starting BoursiercomCrawler with ID:" + str(self.threadID))
        self.status = "running"
        client = boto3.client('firehose', region_name='us-east-1')
        stream_name = "custom-boursiercom-" + str(self.threadID)
        try:
            self.create_stream(client, stream_name)
            print('Creating Boursiercom Kinesis stream... Please wait...')
            time.sleep(40)
        except:
            print("Failed to create" + stream_name)
            return

        stream_status = client.describe_delivery_stream(DeliveryStreamName=stream_name)
        if stream_status['DeliveryStreamDescription']['DeliveryStreamStatus'] == 'ACTIVE':
            print("\n ==== KINESES " + stream_name + " ONLINE ====")


        settings = Settings({
            'ITEM_PIPELINES': {
                'crawler.datasources.spider.boursiercom_spider.JsonWriterPipeline': 100,
            },
            'SPIDER_MIDDLEWARES' : {
                'crawler.datasources.spider.boursiercom_spider.SpiderMiddleware': 543,
            },
            # Wait 2 seconds before each page scrape
            'DOWNLOAD_DELAY': 2,
            'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            'COOKIES_ENABLED': False

        })

        # TO DEBUG:
        configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})

        print('Starting streaming '+ stream_name)
        while True:
            if self.status != "running":
                # We will be able to manage pausing the thread here
                print("Got stop signal for Boursiercom crawler " + stream_name)
                self.delete_stream(client, stream_name)
                break
            try:
                print("Boursiercom crawling ...")
                runner = CrawlerRunner(settings)
                runner.crawl(BoursierCom, client, stream_name)
                time.sleep(3600)
                print('Waiting 1 hour before scraping Boursiercom again')
            except:
                time.sleep(30)
                print('Waiting 1 hour before scraping Boursiercom again')
                pass



        self.status = "finished"



    def create_stream(self,client, stream_name):
        return client.create_delivery_stream(
            DeliveryStreamName=stream_name,
            S3DestinationConfiguration={
                'RoleARN': 'arn:aws:iam::896256228786:role/firehose_delivery_role',
                'BucketARN': 'arn:aws:s3:::kinesiscustomstream',
                'Prefix': stream_name + '//'
            }
        )

    def delete_stream(self, client, stream_name):
        try:
            print('Successfully delete kinesis stream: {}'.format(stream_name))
            return client.delete_delivery_stream(DeliveryStreamName=stream_name)
        except:
            print('Kinesis {} does not exist'.format(stream_name))