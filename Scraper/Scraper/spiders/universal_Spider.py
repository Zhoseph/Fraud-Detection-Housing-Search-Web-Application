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
from pygeocoder import Geocoder
from state.StateName import states as states
from httplib2 import Http

uiEmailUrl = "http://54.175.222.115:8888/fraud_report"

class universalSpider(CrawlSpider):
    name = "universalSpider"
    start_urls = []
    email_address = ""

    def __init__(self, *args, **kwargs):
        super(universalSpider, self).__init__(*args, **kwargs)
        self.start_urls.append(kwargs.get('url'))
        self.email_address = kwargs.get('email_address')

    def parse(self, response):
        log.msg(
            u'Parsing URL is {0}'.format(
                response.url),
            level=log.INFO)
        if 'apartments' in response.url:
            yield scrapy.Request(response.url, callback=self.parse_listing_apartments)
        elif 'craigslist' in response.url:
            yield scrapy.Request(response.url, callback=self.parse_listing_craig)
        elif 'trulia' in response.url:
            yield scrapy.Request(response.url, callback=self.parse_listing_trulia)
        elif 'hotpads' in response.url:
            yield scrapy.Request(response.url, callback=self.parse_listing_hotpads)
        else:
            http_obj = Http()
            resp, content = http_obj.request(
                uri=uiEmailUrl,
                method='POST',
                headers={'Content-Type': 'application/json; charset=UTF-8'},
                body=json.dumps({"error" : "We only support apartments, craigslist, trulia and hotpads"}),
            )

    def parse_listing_hotpads(self, response):
        rentalList = ListingItem()
        WEBSITE = "Hotpads"
        content = response.xpath('//script[@data-react-helmet="true" and contains(text(),"PostalAddress")]/text()').extract_first()
        if content is None:
            return
        listingJson = json.loads(content)
        parseurl = response.url.split('-')
        pid = parseurl[len(parseurl) - 1].split('/')
        rentalList['pid'] = pid[0]
        if rentalList['pid'] is None:
            return
        dateText = ''
        UpdateDtText = response.xpath('//span[@class="Text Utils-accent-dark Text-tiny Text-xlAndUp-sm" and contains(text(), "Updated")]/text()').extract_first()
        PostDtText = response.xpath('//span[@class="Text Utils-accent-dark Text-tiny Text-xlAndUp-sm" and contains(text(), "Posted")]/text()').extract_first()
        updatetime = ''
        if UpdateDtText is None:
            dateText = PostDtText
        else:
            dateText = UpdateDtText
        if dateText is not None:
            updatedDt = dt.now()
            if dateText.find("minutes") > -1:
                updatedDt = updatedDt - timedelta(minutes=int(dateText.split(' ')[1]))
            elif dateText.find("hour") > -1:
                updatedDt = updatedDt - timedelta(hours=int(dateText.split(' ')[1]))
            elif dateText.find("day") > -1:
                updatedDt = updatedDt - timedelta(days=int(dateText.split(' ')[1]))
            elif dateText.find("month") > -1:
                updatedDt = updatedDt - timedelta(days=int(dateText.split(' ')[1])*30)
            updatetime = updatedDt.strftime("%Y-%m-%d %H:%M")
        rentalList['dt'] = updatetime
        rentalList['website'] = WEBSITE
        rentalList['listid'] = WEBSITE + rentalList['pid']
        rentalList['url'] = response.url
        rentalList['title'] = response.xpath('//title[@data-react-helmet="true"]/text()').extract_first()
        addressAttributes = listingJson['@graph'][0]
        listAttributes = listingJson['@graph'][1]
        rentalList['price'] = listAttributes['offers']['price']
        bedsText = response.xpath('//span[@class="Text BedsBathsSqft-text Text-sm Text-xlAndUp-md" and contains(text(),"bed")]/text()').extract_first()
        if bedsText is not None:
            bedsText = bedsText.split(" ")[0].replace("-","")
            rentalList['bedroom'] = int(bedsText)
        else:
            rentalList['bedroom'] = ''
        areaText = response.xpath('//span[@class="Text BedsBathsSqft-text Text-sm Text-xlAndUp-md" and contains(text(),"sqft")]/text()').extract_first()
        if areaText is not None:
            areaText = areaText.split(" ")[0].replace(",","").replace('-', '')
            if len(areaText) > 0:
                rentalList['area'] = float(areaText)
            else:
                rentalList['area'] = ''
        else:
            rentalList['area'] = ''
        rentalList['hood'] = ''
        descriptionText = response.xpath('//div[@id="HdpDescriptionContent"]/text()').extract_first()
        if descriptionText is not None:
            rentalList['description'] = " ".join(descriptionText.split())
        else:
            rentalList['description'] = ''
        rentalList['isFlagged'] = ''
        rentalList['isRemoved'] = ''
        rentalList['accuracy'] = ''
        rentalList['agent'] = ''
        rentalList['contact'] = ''

        rentalList['address'] = {
            "address" : "",
            "street" : addressAttributes['address']['streetAddress'],
            "city" : addressAttributes['address']['addressLocality'],
            "state" :  states[addressAttributes['address']['addressRegion']],
            "zipcode" : addressAttributes['address']['postalCode'],
            "lat" : addressAttributes['geo']['latitude'],
            "lon" : addressAttributes['geo']['longitude']
            }
        imgTree = response.xpath('//img[@class="ImageLoader Carousel-item"]')
        imageSet = []
        # Sometimes there's no location info, and no map on the page
        if len(imgTree) > 0:
            for image in imgTree:
                url = image.xpath('./@src').extract_first()
                imageSet.append(url)
        rentalList['image'] = imageSet
        yield rentalList

    def parse_listing_apartments(self, response):
        WEBSITE = "Apartments"
        rentalList = ListingItem()
        try:
            rentalList['pid'] = response.xpath('//main/@data-listingid').extract_first()
            rentalList['website'] = WEBSITE
            rentalList['listid'] = WEBSITE + rentalList['pid']
            rentalList['repostId'] = rentalList['pid']
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
            if beds is not None:
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
                    "address": "",
                    "street": response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first(),
                    "city": response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first(),
                    "state": states[response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()],
                    "zipcode": response.xpath('//span[@itemprop="postalCode"]/text()').extract_first(),
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
                    "address": "",
                    "street": response.xpath('//meta[@itemprop="streetAddress"]/@content').extract_first(),
                    "city": response.xpath('//meta[@itemprop="addressLocality"]/@content').extract_first(),
                    "state": states[response.xpath('//meta[@itemprop="addressRegion"]/@content').extract_first()],
                    "zipcode": response.xpath('//meta[@itemprop="postalCode"]/@content').extract_first(),
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
                            # Skip listing if there are problems parsing it
            log.msg(
            u'Error happens : {0}'.format(
                    e),
            level=log.ERROR)

        yield rentalList

    def parse_listing_craig(self, response):
        WEBSITE = "Craiglist"
        rentalList = ListingItem()
        try:
            postinfo = response.xpath('//div[@class="postinginfos"]')[0]
            postid = postinfo.xpath('.//p[@class="postinginfo"]/text()').extract_first()
            if postid is not None:
                pd = postid.split(":")[1].strip()
            else:
                urlArray = response.url.split("/")
                pd = urlArray[len(urlArray) -1].split('.')[0]
            rentalList['pid'] = pd
            rentalList['repostId'] = ''
            dt = postinfo.xpath('.//time[@class="timeago"]/text()').extract_first()
            item_ts = ''
            if dt is not None:
                item_ts = datetime.datetime.strptime(dt, "%Y-%m-%d  %I:%M%p").strftime('%Y-%m-%d %H:%M')
            rentalList['dt'] =  item_ts
            rentalList['url'] = response.url
            listinginfo = response.xpath('//span[@class="postingtitletext"]')[0]
            price = ''
            priceText = listinginfo.xpath('.//span[@class="price"]/text()').extract_first()
            if priceText is not None:
                price = int(priceText.strip('$'))
            rentalList['price'] = price
            rentalList['title'] = response.xpath('//meta[@property="og:title"]/@content').extract_first()
            housingElement = listinginfo.xpath('.//span[@class="housing"]/text()').extract_first()
            beds = ''
            sqft = ''
            if housingElement is not None:
                bedsqft = self._get_list_str(housingElement)
                beds = int(self._get_int_prefix(bedsqft, "br"))  # appears as "1br" to "8br" or missing
                sqft = float(self._get_int_prefix(bedsqft, "ft"))  # appears as "000ft" or missing
            rentalList['bedroom'] = beds
            rentalList['area'] = sqft
            hoodelement = listinginfo.xpath('.//small/text()').extract_first()
            hood = ''
            if hoodelement is not None:
                hood = hoodelement.strip(' ()')
            rentalList['hood'] = hood
            rentalList['listid'] = WEBSITE + rentalList['pid']
            rentalList['website'] = WEBSITE
            rentalList['agent'] = ''
            rentalList['contact'] = ''
            lat = ''
            lng = ''
            accuracy = ''
            street_address = ''
            city = ''
            state = ''
            post_code = ''

            map = response.xpath('//div[@id="map"]')

            # Sometimes there's no location info, and no map on the page
            if len(map) > 0:
                lat = float(map[0].xpath('./@data-latitude').extract_first())
                lng = float(map[0].xpath('./@data-longitude').extract_first())
                accuracy = map[0].xpath('./@data-accuracy').extract_first()
                results = Geocoder.reverse_geocode(lat, lng)
                city = results.city
                street_address = results.street_number + ' ' + results.route
                state = results.administrative_area_level_1
                post_code  = results.postal_code
            descList = response.xpath('//section[@id="postingbody"]/text()').extract()
            description = ''
            if descList is not None:
                #description = self._get_list_str(descList).rstrip()
                description = " ".join(self._get_list_str(descList).split())
            if len(description) == 0:
                descriptionArray = response.xpath('//section[@id="postingbody"]/p/text()').extract()
                description = " ".join(self._get_list_str(descriptionArray).split())
            # removed
            isRemoved = False
            removedElement = response.xpath('//div[@class="removed"]')
            if len(removedElement) > 0:
                isRemoved = True

            isFlagged = False
            flagList = response.xpath('//aside[@class="flags done"]')
            if len(flagList) > 0:
                flagTextList = flagList[0].xpath('/span[@class="flagtext"]/text()').extract_first()
                if flagTextList is not None and flagTextList == 'prohibited':
                    isFlagged = True

            imgTree = response.xpath('//a[@class="thumb"]')
            imageSet = []
            # Sometimes there's no location info, and no map on the page
            if len(imgTree) > 0:
                for image in imgTree:
                    url = image.xpath('./@href').extract_first()
                    imageSet.append(url)

            rentalList['description'] = description
            rentalList['isFlagged'] = isFlagged
            rentalList['isRemoved'] = isRemoved
            rentalList['accuracy'] = accuracy
            rentalList['image'] = imageSet
            rentalList['address'] = {
                "address" : "",
                "street" : street_address,
                "city" : city,
                "state" :  state,
                "zipcode" : post_code,
                "lat" : lat,
                "lon" : lng

            }
            yield rentalList

        except Exception, e:
            log.msg(
            u'Error happens in parse items: {0}'.format(
                    e),
            level=log.ERROR)
            return

    def _get_list_str(self, descList):
        allStr = ''.join(descList)
        allStr = allStr.rstrip()
        allStr = allStr.lstrip()
        return allStr

    def parse_listing_trulia(self, response):
        WEBSITE = "Trulia"
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
                rentalList['listid'] = WEBSITE + rentalList['pid']
                rentalList['website'] = WEBSITE
                rentalList['repostId'] = trulia_json['id']
                dateUpdatedText = hxs.xpath('//span[contains(text(),"Information last updated on")]/text()').extract_first()
                date = ''
                if dateUpdatedText is not None:
                    dateupdated = " ".join(dateUpdatedText.split())
                    datetext = dateupdated.split(" ")[4] + " " + dateupdated.split(" ")[5] + " " + dateupdated.split(" ")[6]
                    date = datetime.datetime.strptime(datetext, "%m/%d/%Y %I:%M %p").strftime('%Y-%m-%d %H:%M')
                rentalList['dt'] = date
                rentalList['title'] = trulia_json['shortDescription']
                rentalList['price'] = trulia_json['price']
                rentalList['bedroom'] = int(trulia_json['numBedrooms'])
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
                imageTree = hxs.xpath('//div[@id="photoPlayerSlideshow"]/@data-photos').extract_first()
                imageSet = []
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

    def _get_int_prefix(self, str, label):
        '''
        Bedrooms and square footage have the format "xx 1br xx 450ft xx". This helper
        function extracts relevant integers from strings of this format.
        '''

        for s in str.split(' '):
            if label in s:
                return s.strip(label)

        return 0