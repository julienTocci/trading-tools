import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
import json
import boto3
import re
from scrapy.http import Request


# Using multiple urls will put the data in the same S3 file, hence when we get the last json object to have the last values, we will miss
# the last-1 object with the values from the second url
target_urls =  ['https://www.boursier.com/indices/cours/cac-40-FR0003500008,FR.html']
                  #,'https://www.boursier.com/indices/cours/dow-jones-industrial-US2605661048,US.html']


class pageItem(scrapy.Item):
    title = scrapy.Field()
    highest_capitalization_urls = scrapy.Field()
    highest_capitalization_names = scrapy.Field()
    highest_capitalization_values = scrapy.Field()

    opening = scrapy.Field()
    highest = scrapy.Field()
    lowest = scrapy.Field()

    increase_decrease_titles = scrapy.Field()
    increase_decrease_values = scrapy.Field()
    increase_decrease_gain = scrapy.Field()

    variation_sessions = scrapy.Field()
    variation_session_variation = scrapy.Field()
    cotations_history = scrapy.Field()
    other_numbers = scrapy.Field()
    actualities_url = scrapy.Field()
    actualities = scrapy.Field()


# The following is not used but can be usefull for other use cases of scrapy
class SpiderMiddleware(object):

    def process_spider_output(self, response, result, spider):
        toto = []
        for x in result:
        #    if isinstance(x, pageItem):
        #        print("LALA")
            yield x

# Pipeline
class JsonWriterPipeline(object):
    def __init__(self):
        self.kinesis = None #boto3.client('firehose', region_name='us-east-1')
        self.stream_name = ""


    def open_spider(self, spider):
        self.stream_name = spider.stream_name
        self.kinesis = spider.kinesis_client


    def process_item(self, item, spider):
        # Write directly to s3 here
        line = json.dumps(dict(item)) + ",\n"
        self.kinesis.put_record(DeliveryStreamName=self.stream_name,
                                Record={'Data': line})

        return item



class BoursierCom(scrapy.Spider):
    name = "boursiercom"
    def __init__(self, client=None, stream_name=None, *args, **kwargs):
        super(BoursierCom, self).__init__(*args, **kwargs)
        self.stream_name = stream_name
        self.kinesis_client = client

    def start_requests(self):
        urls = target_urls
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse_actuality_page(self, response):
        # A scraper designed to operate on the article page
        # actuality_body = response.xpath('//p/text()').getall() Does not get tag inside <p> tags => we are missing important information
        # Improvments: https://stackoverflow.com/questions/28160445/extracting-paragraph-text-including-other-elements-content-using-scrapy-selecto


        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text)
        actuality_body = [p.get_text().strip() for p in soup.find_all('p')]

        item = response.meta['item']  # retrieve item generated in previous request
        article = dict()

        actuality_body = ''.join(actuality_body)

        # To remove all space
        body = actuality_body.replace(u'\xa0', u' ')

        # Clear html tags from string:
        cleanr = re.compile('<.*?>')

        # Remove text transorfmations
        regex = re.compile(r'[\n\r\t]')

        body_cleaned = re.sub(cleanr, '', body)
        body_cleaned = regex.sub(" ", body_cleaned)

        article['title'] = response.xpath('//title/text()').get()
        article['body'] = str(body_cleaned)
        item['actualities'].append(article)

        # check if we have any more agent urls left
        actualities_url = response.meta['actualities_url']
        if not actualities_url:  # we crawled all of the agents!
            yield item
            return
        # if we do - crawl next agent and carry over our current item
        url = 'https://www.boursier.com/indices' + actualities_url.pop(0)
        yield Request(url, callback=self.parse_actuality_page,
                      meta={'item': item, 'actualities_url' : item['actualities_url']})

    def parse(self, response):
        item = pageItem()  # Creating a new Item object

        item['title'] = response.xpath('//title/text()').get()
        item['highest_capitalization_urls'] = response.xpath('//div[@class=" tables first"]/div/table/tbody/tr/td/b/a/@href').getall()
        item['highest_capitalization_names'] = response.xpath('//div[@class=" tables first"]/div/table/tbody/tr/td/b/a/text()').getall()
        item['highest_capitalization_values'] = response.xpath('//div[@class=" tables first"]/div/table/tbody/tr/td[2]/text()').getall()

        item['opening'] = response.xpath('//div[@class="table--wrapper top--margin"]/table/tbody/tr/td/strong/text()').getall()[0]
        item['highest'] = response.xpath('//div[@class="table--wrapper top--margin"]/table/tbody/tr/td/strong/text()').getall()[1]
        item['lowest'] = response.xpath('//div[@class="table--wrapper top--margin"]/table/tbody/tr/td/strong/text()').getall()[2]

        item['increase_decrease_titles'] = response.xpath('//div[@class="col col-6 col--equals small-12"]/div/table/tbody/tr/td/a/text()').getall()
        item['increase_decrease_values'] = response.xpath('//div[@class="col col-6 col--equals small-12"]/div/table/tbody/tr/td/text()').getall()
        item['increase_decrease_gain'] = response.xpath('//div[@class="col col-6 col--equals small-12"]/div/table/tbody/tr/td/b/text()').getall()

        item['variation_sessions'] = response.xpath('//div[@class="scrolly-table"]/table/tbody/tr/td/text()').getall()
        item['variation_session_variation'] = response.xpath('//div[@class="scrolly-table"]/table/tbody/tr/td/b/text()').getall()
        item['cotations_history'] = response.xpath('//table[@class="table table--first-col-regular table--last-col-right"]/tbody/tr/td/b/text()').getall()
        item['other_numbers'] = response.xpath('//div[@class="col col-6 small-12 col--equals"]/table[@class="table table--last-col-right table--no-margin"]/tbody/tr/td/b/text()').getall()

        item['actualities_url'] = response.xpath('//div[@class="news-list"]/div/div/div/a/@href').getall()
        item["actualities"] = []

        url = 'https://www.boursier.com/indices' + item['actualities_url'].pop(0)
        # we want to go through agent urls one-by-one and update single item with agent data
        yield Request(url, callback=self.parse_actuality_page,
                      meta={'item': item, 'actualities_url' : item['actualities_url']})

