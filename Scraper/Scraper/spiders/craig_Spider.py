from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime
from datetime import timedelta
import datetime
import scrapy
from scrapy.linkextractors import LinkExtractor
from Scraper.items import ListingItem
from pygeocoder import Geocoder
from scrapy import log

# start_date = "2017-06-27 13:00"
# earliest_ts = datetime.datetime.strptime(start_date, "%Y-%m-%d %H:%M")
# latest_ts=earliest_ts + timedelta(hours=96.0)
WEBSITE = "Craiglist"


class MySpider(CrawlSpider):
    name = "craig"
    allowed_domains = [
        "sfbay.craigslist.org",
        "bakersfield.craigslist.org",
        "fresno.craigslist.org",
        "goldcountry.craigslist.org",
        "chico.craigslist.org",
        "humboldt.craigslist.org",
        "oregoncoast.craigslist.org",
        "sacramento.craigslist.org",
        "monterey.craigslist.org",
        "santabarbara.craigslist.org",
        "sandiego.craigslist.org",
        "losangeles.craigslist.org"
    ]
    start_urls = [
        'https://sfbay.craigslist.org/search/apa',
        "https://bakersfield.craigslist.org/search/apa",
        "https://fresno.craigslist.org/search/apa",
        "https://goldcountry.craigslist.org/search/apa",
        "https://chico.craigslist.org/search/apa",
        "https://humboldt.craigslist.org/search/apa",
        "https://oregoncoast.craigslist.org/search/apa",
        "https://sacramento.craigslist.org/search/apa",
        "https://monterey.craigslist.org/search/apa",
        "https://santabarbara.craigslist.org/search/apa",
        "https://sandiego.craigslist.org/search/apa",
        "https://losangeles.craigslist.org/search/apa"]

    rules = (Rule(LinkExtractor(restrict_xpaths=('//a[@title="next page"]')), callback="parse_rows", follow=True),)
    earliest_ts = ''
    latest_ts = ''

    def __init__(self, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.earliest_ts = datetime.datetime.strptime(kwargs.get('start_date'), "%Y-%m-%d %H:%M")
        self.latest_ts = datetime.datetime.strptime(kwargs.get('end_date'), "%Y-%m-%d %H:%M")

    def _get_first_str(self, strList):
        '''
        The xpath() function returns a list of items that may be empty. Most of the time,
        we want the first of any strings that match the xml query. This helper function
        returns that string, or null if the list is empty.
        '''

        if len(strList) > 0:
            return strList[0]

        return ''

    def _get_list_str(self, descList):
        allStr = ''.join(descList)
        allStr = allStr.rstrip()
        allStr = allStr.lstrip()
        return allStr

    def _get_int_prefix(self, str, label):
        '''
        Bedrooms and square footage have the format "xx 1br xx 450ft xx". This helper
        function extracts relevant integers from strings of this format.
        '''

        for s in str.split(' '):
            if label in s:
                return s.strip(label)

        return 0

    def parse_rows(self, response):
        for item in response.xpath('//ul[@class="rows"]/li[@class="result-row"]'):
            try:
                repostId = ''
                dt = ''
                title = ''
                price = ''
                beds = ''
                sqft = ''
                hood = ''
                pid = item.xpath('./@data-pid').extract_first()  # post id, always present
                if item.xpath('./@data-repost-of'):
                    repostId = item.xpath(
                        './@data-repost-of').extract_first()  # pid of the original ad, may not be present

                    # Extract two lines of listing info, always present
                line1 = item.xpath('.//p[@class="result-info"]')[0]
                line2 = line1.xpath('.//span[@class="result-meta"]')[0]

                dt = line1.xpath('.//time/@datetime').extract_first()  # always present
                if dt is None:
                    continue
                item_ts = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M")
                if item_ts > self.latest_ts:
                    continue
                elif item_ts < self.earliest_ts:
                    break
                url = line1.xpath('.//a/@href').extract_first()  # always present
                title = line1.xpath('.//a[@class = "result-title hdrlnk"]/text()').extract_first()
                # price
                priceElement = line2.xpath('.//span[@class="result-price"]/text()').extract_first()
                if priceElement is not None:
                    price = int(priceElement.strip('$'))
                    # neighborhood
                hoodElement = line2.xpath('.//span[@class="result-hood"]/text()').extract_first()
                if hoodElement is not None:
                    hood = hoodElement.strip(' ()')
                    # housing
                housingElement = line2.xpath('.//span[@class="housing"]/text()').extract_first()
                if housingElement is not None:
                    bedsqft = self._get_list_str(housingElement)
                    beds = int(self._get_int_prefix(bedsqft, "br"))  # appears as "1br" to "8br" or missing
                    sqft = float(self._get_int_prefix(bedsqft, "ft"))  # appears as "000ft" or missing
                item_url = response.url.split('/search')[0] + url
                yield scrapy.Request(item_url, callback=self.parse_items,
                                     meta={'pid': pid, 'repostId': repostId, 'dt': dt, 'title': title, 'price': price,
                                           'beds': beds, 'sqft': sqft, 'hood': hood})
            except Exception, e:
                log.msg(
                    u'Error happens in parse_rows : {0}'.format(
                        e),
                    level=log.WARNING)
                continue

    def parse_items(self, response):
        rentalList = ListingItem()
        try:
            rentalList['pid'] = response.meta['pid']
            rentalList['repostId'] = response.meta['repostId']
            rentalList['dt'] = response.meta['dt']
            rentalList['url'] = response.url
            rentalList['title'] = response.meta['title']
            rentalList['price'] = response.meta['price']
            rentalList['bedroom'] = response.meta['beds']
            rentalList['area'] = response.meta['sqft']
            rentalList['hood'] = response.meta['hood']
            rentalList['listid'] = WEBSITE + response.meta['pid']
            rentalList['website'] = WEBSITE
            lat = ''
            lng = ''
            accuracy = ''
            street_address = ''
            city = ''
            state = ''
            post_code = ''

            map = response.xpath('//div[@id="map"]')
            print
            # Sometimes there's no location info, and no map on the page
            if len(map) > 0:
                lat = float(map[0].xpath('./@data-latitude').extract_first())
                lng = float(map[0].xpath('./@data-longitude').extract_first())
                accuracy = map[0].xpath('./@data-accuracy').extract_first()
                results = Geocoder.reverse_geocode(lat, lng)
                city = results.city
                state = results.administrative_area_level_1
                post_code = results.postal_code
                street = response.xpath('//div[@class="mapaddress"]/text()').extract_first()
                if street is not None:
                    street_address = street
                else:
                    street_address = results.street_number + ' ' + results.route
            descList = response.xpath('//section[@id="postingbody"]/text()').extract()
            description = ''
            if descList is not None:
                # description = self._get_list_str(descList).rstrip()
                description = " ".join(self._get_list_str(descList).split())
            if len(description) == 0:
                descriptionArray = response.xpath('//section[@id="postingbody"]/p/text()').extract()
                if descriptionArray is not None:
                    description = " ".join(self._get_list_str(descriptionArray).split())
            # removed
            isRemoved = False
            removedElement = response.xpath('//div[@class="removed"]')
            if len(removedElement) > 0:
                isRemoved = True
            print "length of removedElement is" + str(len(removedElement))
            isFlagged = False
            flagList = response.xpath('//aside[@class="flags done"]')
            if len(flagList) > 0:
                flagTextList = flagList[0].xpath('./span[@class="flagtext"]/text()').extract_first()
                if flagTextList is not None and flagTextList == 'prohibited':
                    isFlagged = True
            print "length of flagTextList is" + str(len(flagTextList))
            imgTree = response.xpath('//a[@class="thumb"]')
            imageSet = []
            # Sometimes there's no location info, and no map on the page
            if len(imgTree) > 0:
                for image in imgTree:
                    url = image.xpath('./@href').extract_first()
                    imageSet.append(url)
            print "length of imageTree is" + str(len(imgTree))
            rentalList['description'] = description
            rentalList['isFlagged'] = isFlagged
            rentalList['isRemoved'] = isRemoved
            rentalList['accuracy'] = accuracy
            rentalList['image'] = imageSet
            rentalList['agent'] = ''
            rentalList['contact'] = ''
            rentalList['address'] = {
                "address": "",
                "street": street_address,
                "city": city,
                "state": state,
                "zipcode": post_code,
                "lat": lat,
                "lon": lng
            }
            print rentalList
            yield rentalList

        except Exception, e:
            log.msg(
                u'Error happens in parse items: {0}'.format(
                    e),
                level=log.WARNING)
            # Skip listing if there are problems parsing it
            return


