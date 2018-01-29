from scrapy.spiders import CrawlSpider
import scrapy
from datetime import datetime as dt
from datetime import timedelta
from scrapy.spiders import Rule, CrawlSpider
from scrapy.selector import Selector
from Scraper.items import ListingItem
import re
import json
import requests
from scrapy import log
import datetime
from state.StateName import states as states
WEBSITE = "Apartments"
#START_DATE = "2017-07-01 13:00"                
#TIME = datetime.datetime.strptime(START_DATE, "%Y-%m-%d %H:%M")

class ApartmentsSpider(CrawlSpider):
	name = "Apartments"
	allowed_domains = ["www.apartments.com"]
	start_urls = ["https://www.apartments.com/"]
	TIME = ''
	END = ''
	
	def __init__(self, *args, **kwargs):
		super(ApartmentsSpider, self).__init__(*args, **kwargs)
		self.TIME = datetime.datetime.strptime(kwargs.get('start_date'), "%Y-%m-%d %H:%M")
		self.END = datetime.datetime.strptime(kwargs.get('end_date'), "%Y-%m-%d %H:%M")
    
	def last_pagenumber_in_search(self, response):
		try:
			pageList = response.xpath('//div[@id="paging"]//a/text()').extract()
			length = len(pageList)
			last_page = int(pageList[length - 3])
			return last_page
		except:
			return 1
	
	def parse(self, response):
		for t in response.xpath('//ul[@class="submenu"]')[1:]:
			for x in t.xpath('.//li'):
				url = x.xpath('.//a/@href').extract_first()
				print "parse:" + url
				yield scrapy.Request(url,callback=self.parsePage)
	    
	def parsePage(self,response):
		last_page_number = self.last_pagenumber_in_search(response)

		page_urls = [response.url]
		for pageNumber in range(2, last_page_number + 1):
			page_urls = page_urls + [response.url + str(pageNumber) + "/"]
		for page_url in page_urls:	
			print "parsePage: " + page_url
			yield scrapy.Request(page_url,callback=self.parse_listing_results_page)
    
	def parse_listing_results_page(self, response):
		for article in response.xpath('//article[contains(@class,"placard")]'):
			listingUrl = article.xpath('./@data-url').extract_first()
			listingid = article.xpath('./@data-listingid').extract_first()
			dtText = article.xpath('.//span[@class = "listingFreshness"]//span//span/text()').extract_first()
			if dtText.find("New") > -1:
				updatedDt = dt.now()
			elif dtText.find("hrs") > -1:
				updatedDt = dt.now() - timedelta(hours=int(dtText.split(' ')[0]))
			elif dtText.find("DAY") > -1:
				updatedDt = dt.now() - timedelta(days=int(dtText.split(' ')[0]))
			else:
				continue
			if updatedDt < self.TIME:
				log.msg(
                    u'Listing {0} is out of date, skipped'.format(
                    	listingid),
                    	level=log.INFO)				
				continue
			if updatedDt > self.END:
				log.msg(
					u'Listing {0} is for ahead of date, skipped'.format(
						listingid),
					level=log.INFO)
			updatedDt = updatedDt.strftime("%Y-%m-%d %H:%M")
			yield scrapy.Request(listingUrl, callback=self.parse_listing_contents,  meta={'listingid': listingid, 'updatedDt': updatedDt})

	def parse_listing_contents(self, response):
		rentalList = ListingItem()
		try:
			rentalList['pid'] = response.request.meta['listingid']
			rentalList['website'] = WEBSITE
			rentalList['listid'] = WEBSITE + rentalList['pid']
			rentalList['repostId'] = rentalList['pid']
			rentalList['dt'] = response.request.meta['updatedDt']
			rentalList['title'] = response.xpath('//meta[@property="og:title"]/@content').extract_first()
			priceArray = response.xpath('//td[@class="rent"]/text()').extract_first()
			if priceArray is not None:
				priceText = ''.join(priceArray)
				price = " ".join(priceText.split())
				rentalList['price'] = int(price.strip('$').replace(",", ""))
			else:
				rentalList['price'] = ''
			bedsPart = response.xpath('//span[@class="rentRollup"]')[0]
			beds = bedsPart.xpath('.//span[@class="longText"]/text()').extract_first()
			if beds is not None and ' ' in beds:
				rentalList['bedroom'] = int(beds.split(' ')[0])
			else:
				rentalList['bedroom'] = ''
			sqft = response.xpath('//td[@class="sqft"]/text()').extract_first()
			if sqft is not None:
				rentalList['area'] = float(sqft.split(' ')[0].replace(",", ""))
			else:
				rentalList['area'] = ''
			rentalList['hood'] = response.xpath('//a[@class="neighborhood"]/text()').extract_first()
			agentInfo = response.xpath('//div[@class="contactInfo"]')[0]
			if agentInfo is None:
				agentArray = None
				contactArray = None
			agentArray = agentInfo.xpath('.//div/text()').extract_first()
			agent = ''
			if agentArray is not None:
				agentText = ''.join(agentArray)
				agent = " ".join(agentText.split())
			rentalList['agent'] = agent
			contact = ''
			contactArray = agentInfo.xpath('.//div[@class="phoneNumber"]/text()').extract()
			if contactArray is not None:
				contactText = ''.join(contactArray)
				contact = " ".join(contactText.split())
			rentalList['contact'] = contact
			rentalList['url'] = response.url
			rentalList['isFlagged'] = False
			rentalList['isRemoved'] = False
			descriptionArray = response.xpath('//p[@itemprop="description"]/text()').extract()
			description = ''
			if descriptionArray is not None:
				descriptionText = ''.join(descriptionArray)
				description = " ".join(descriptionText.split())
			rentalList['description'] = description
			address = response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first()
			lat = ''
			lon = ''
			if address is not None:
				latText = response.xpath('//meta[@property="place:location:latitude"]/@content').extract_first()
				if latText is not None:
					lat = float(latText)
				lonText = response.xpath('//meta[@property="place:location:longitude"]/@content').extract_first()
				if lonText is not None:
					lon = float(lonText)
				rentalList['address'] = {
					"address" : "",
                    "street" : response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first(),
                    "city" : response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first(),
                    "state" :  states[response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()],
                    "zipcode" : response.xpath('//span[@itemprop="postalCode"]/text()').extract_first(),
                    "lat": lat,
                    "lon": lon
                    
            	}
			else:
				latText = response.xpath('//meta[@property="place:location:latitude"]/@content').extract_first()
				if latText is not None:
					lat = float(latText)
				lonText = response.xpath('//meta[@property="place:location:longitude"]/@content').extract_first()
				if lonText is not None:
					lon = float(lonText)
				rentalList['address'] = {
            		"address" : "",
                    "street" : response.xpath('//meta[@itemprop="streetAddress"]/@content').extract_first(),
                    "city" : response.xpath('//meta[@itemprop="addressLocality"]/@content').extract_first(),
                    "state" : states[response.xpath('//meta[@itemprop="addressRegion"]/@content').extract_first()],
                    "zipcode" : response.xpath('//meta[@itemprop="postalCode"]/@content').extract_first(),
                    "lat": lat,
                    "lon": lon
				}
			imageUl = response.xpath('//ul[@id="fullCarouselCollection"]')
			imageSet = []
			if len(imageUl) > 0:
				for x in imageUl.xpath('.//li'):
					imageSet.append(x.xpath('.//img/@src').extract_first())
			rentalList['image'] = imageSet
		except Exception, e:
			log.msg(
				u'Error happens : {0}'.format(
				e),
            level=log.WARNING)
		yield rentalList