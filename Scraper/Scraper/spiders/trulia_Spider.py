from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime as dt
from datetime import timedelta
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from Scraper.items import ListingItem
import re
import json
import requests
import logging
from scrapy import log
import datetime
from datetime import datetime as dt

WEBSITE = "Trulia"
#START_DATE = "2017-07-20 13:00"                
#TIME = datetime.datetime.strptime(START_DATE, "%Y-%m-%d %H:%M")

class TruliaSpider(CrawlSpider):
    handle_httpstatus_list = [301]
    name = "Trulia"
    allowed_domains = ["www.trulia.com"]
    start_urls = ["https://www.trulia.com/rent-sitemap/"]
    TIME = ''
    END = ''

    def __init__(self, *args, **kwargs):
        super(TruliaSpider, self).__init__(*args, **kwargs)
        self.TIME = datetime.datetime.strptime(kwargs.get('start_date'), "%Y-%m-%d %H:%M")
        self.END = datetime.datetime.strptime(kwargs.get('end_date'), "%Y-%m-%d %H:%M")

    rules = (
        Rule(LinkExtractor(allow='https://www.trulia.com/rent-sitemap/.*'), follow= True ),
        Rule(LinkExtractor(allow='https://www.trulia.com/rental/.*'), callback='parse_items', follow= True),
    )

    def parse_items(self, response):
        rentalList = ListingItem()
        try:
            hxs = Selector(response)
            resDetail = response.xpath('//script[@type="text/javascript" and contains(text(),"trulia.propertyData.set")]').extract()
            if resDetail:
                res_list = re.split(';',resDetail[0])
                res_json_list = re.split('trulia.propertyData.set',res_list[3])
                json_content = re.split(',"dataPhotos"',res_json_list[1])
                jsontext = json_content[0].strip("(") + "}"
                trulia_json = json.loads(jsontext)
                rentalList['pid'] = trulia_json['id']
                rentalList['website'] = WEBSITE
                rentalList['repostId'] = trulia_json['id']
                dateUpdatedText = hxs.xpath('//span[contains(text(),"Information last updated on")]/text()').extract_first()
                if dateUpdatedText is not None:
                    dateupdated = " ".join(dateUpdatedText.split())
                    date = dateupdated.split(" ")[4] + " " + dateupdated.split(" ")[5] + " " + dateupdated.split(" ")[6]
                    postdate = datetime.datetime.strptime(date, "%m/%d/%Y %I:%M %p").strftime('%Y-%m-%d %H:%M')
                    rentalList['dt'] = postdate
                else:
                    return
                item_ts = dt.strptime(rentalList['dt'], "%Y-%m-%d %H:%M")
                if item_ts < self.TIME:
                    log.msg(
                    u'Listing {0} is out of date, skipped'.format(
                        rentalList['pid']),
                        level=log.INFO)
                    return
                if item_ts > self.END:
                    log.msg(
                    u'Listing {0} is ahead of date, skipped'.format(
                        rentalList['pid']),
                        level=log.INFO)
                    return
                rentalList['listid'] = WEBSITE + rentalList['pid']
                rentalList['title'] = trulia_json['shortDescription']
                rentalList['price'] = trulia_json['price']
                rentalList['bedroom'] = trulia_json['numBedrooms']
                rentalList['area'] = trulia_json['sqft']
                rentalList['hood'] = trulia_json['neighborhood']
                rentalList['agent'] = trulia_json['agentName']
                rentalList['contact'] = hxs.xpath('//div[@class="property_contact_field h7 man"]/text()').extract_first()
                rentalList['url'] = response.url
                rentalList['isFlagged'] = False
                rentalList['isRemoved'] = False
                descriptionArray = hxs.xpath('//span[@id="corepropertydescription"]/text()').extract()
                description = ''
                if descriptionArray is not None:
                    descriptionText = ''.join(descriptionArray)
                    description = " ".join(descriptionText.split())
                moreDescriptionArray = hxs.xpath('//span[@id="moreDescription"]/text()').extract()
                if moreDescriptionArray is not None:
                    moreDescriptionText = ''.join(moreDescriptionArray)
                    moreDescription = " ".join(moreDescriptionText.split())
                    descriptionNew = description + moreDescription
                    description = descriptionNew.replace('...','')
                rentalList['description'] = description
                rentalList['address'] = {
                    "address" : trulia_json['addressForDisplay'],
                    "street" : re.split(',',trulia_json['addressForDisplay'])[0],
                    "city" : trulia_json['city'],
                    "state" :  trulia_json['stateName'],
                    "zipcode" : trulia_json['zipCode'],
                    "lat": trulia_json['latitude'],
                    "lon" : trulia_json['longitude']
                }
                rentalList['url'] = response.url
                imageSet = []
                imageTree = hxs.xpath('//div[@id="photoPlayerSlideshow"]/@data-photos').extract_first()
                if imageTree is not None:
                    image_Json = json.loads(imageTree)["photos"]
                    front = "http:"
                    for image in image_Json:
                        value = front + image['standard_url']
                        imageSet.append(value)
                rentalList['image'] = imageSet
        except Exception, e:
                            # Skip listing if there are problems parsing it
            log.msg(
                u'Error happens : {0}'.format(
                        e),
                level=log.ERROR)
        
        yield rentalList