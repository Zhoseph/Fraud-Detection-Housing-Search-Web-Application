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
import scrapy
import datetime
from datetime import datetime as dt
from state.StateName import states as states
WEBSITE = "Hotpads"
START_DATE = "2017-07-18 13:00"                
TIME = datetime.datetime.strptime(START_DATE, "%Y-%m-%d %H:%M")

class HotPadsSpider(CrawlSpider):
    handle_httpstatus_list = [301]
    name = "HostPads"
    allowed_domains = ["hotpads.com"]
    start_urls = ["https://hotpads.com/directory-sitemap"]
 
    rules = (
        Rule(LinkExtractor(allow='https://hotpads.com/.*/houses-for-rent')),
        Rule(LinkExtractor(restrict_xpaths=('//link[@rel="next"]')), follow = True),
        Rule(LinkExtractor(allow='https://hotpads.com/.*/pad', restrict_xpaths=('//a[@class="Linker Linker-default"]')), callback='parse_list', follow = True),
    )
    
    def parse_list(self, response):
		rentalList = ListingItem()
		content = response.xpath('//script[@data-react-helmet="true" and contains(text(),"PostalAddress")]/text()').extract_first()
		listingJson = json.loads(content)
		parseurl = response.url.split('-')
		pid = parseurl[len(parseurl) - 1].split('/')
		rentalList['pid'] = pid[0]
		if rentalList['pid'] is None: 
		    return
		dateText = ''
		UpdateDtText = response.xpath('//span[@class="Text Utils-accent-dark Text-tiny Text-xlAndUp-sm" and contains(text(), "Updated")]/text()').extract_first()
		PostDtText = response.xpath('//span[@class="Text Utils-accent-dark Text-tiny Text-xlAndUp-sm" and contains(text(), "Posted")]/text()').extract_first()
		if UpdateDtText is None:
		    dateText = PostDtText
		else:
		    dateText = UpdateDtText
		updatedDt = dt.now()
		if dateText.find("minutes") > -1:
		    updatedDt = updatedDt - timedelta(minutes=int(dateText.split(' ')[1]))
		elif dateText.find("hour") > -1:
		    updatedDt = updatedDt - timedelta(hours=int(dateText.split(' ')[1]))
		elif dateText.find("day") > -1:
		    updatedDt = updatedDt - timedelta(days=int(dateText.split(' ')[1]))
		else:
		    return
		if updatedDt < TIME:
		    return 
		rentalList['dt'] = updatedDt.strftime("%Y-%m-%d %H:%M")
		rentalList['website'] = WEBSITE
		rentalList['listid'] = WEBSITE + rentalList['pid']
		rentalList['url'] = response.url
		rentalList['title'] = response.xpath('//title[@data-react-helmet="true"]/text()').extract_first()
		addressAttributes = listingJson['@graph'][0]
		listAttributes = listingJson['@graph'][1]
		rentalList['price'] = listAttributes['offers']['price']
		rentalList['beds'] = response.xpath('//span[@class="Text BedsBathsSqft-text Text-sm Text-xlAndUp-md" and contains(text(),"bed")]/text()').extract_first().split(" ")[0].replace("-","")
		rentalList['sqft'] = response.xpath('//span[@class="Text BedsBathsSqft-text Text-sm Text-xlAndUp-md" and contains(text(),"sqft")]/text()').extract_first().split(" ")[0].replace(",","").replace('-', '')
		rentalList['hood'] = ''
		descriptionText = response.xpath('//div[@id="HdpDescriptionContent"]/text()').extract_first() 
		rentalList['description'] = " ".join(descriptionText.split()) 
		rentalList['isFlagged'] = ''
		rentalList['isRemoved'] = ''
		rentalList['lat'] = addressAttributes['geo']['latitude']
		rentalList['lng'] = addressAttributes['geo']['longitude']
		rentalList['accuracy'] = ''
		rentalList['agent'] = ''
		rentalList['contact'] = '' 
		
		rentalList['address'] = {
            "address" : "",
            "street_address" : addressAttributes['address']['streetAddress'],
            "city" : addressAttributes['address']['addressLocality'],
            "state" :  states[addressAttributes['address']['addressRegion']],
            "post_code" : addressAttributes['address']['postalCode']
            }
		imgTree = response.xpath('//img[@class="ImageLoader Carousel-item"]')
		imageSet = {}
        # Sometimes there's no location info, and no map on the page
		if len(imgTree) == 0:
		    print("There is no photo!!!")
		i = 0;
		for image in imgTree:
		    url = image.xpath('./@src').extract_first()
		    imageSet[str(i)] = url
		    i = i + 1
		rentalList['images'] = imageSet
		
		yield rentalList
	
 