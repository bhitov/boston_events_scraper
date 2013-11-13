from urllib2 import urlopen
from scrapy.selector import HtmlXPathSelector
from datetime import datetime
from icalendar import Calendar

import arrow

def get_page(url):
    html = urlopen(url).read()
    return HtmlXPathSelector(text=html)

def parse_date_string(date, time):
    d = arrow.get(date, "MMMM D, YYYY").date()
    ts, te = [arrow.get(time_string.strip(), "H:mm a").time() for time_string in time.split('-')]
    return datetime.combine(d, ts), datetime.combine(d, te)

def get_tufts_events():
    hxs = get_page( 'http://www.ece.tufts.edu/research/colloquia/current.php')
    events = hxs.select('//div[@class="colloqitem"]/div[@class="row"]')

    BASE_URL = "http://www.ece.tufts.edu"
    items = []

    for event in events:
        item = {}
        dl_section, desc_section = event.select('div')
        time_section = dl_section.select('div[@class="colloqdate"]/text()').extract()

        item['datetime_start'], item['datetime_end'] = parse_date_string(*time_section)

        item['location'] = dl_section.select('div[@class="colloqplace"]/text()').extract()[0]
        item['title'] = desc_section.select('div[@class="colloqtitle"]/a/text()').extract()[0]
        desc_addr = desc_section.select('div[@class="colloqtitle"]/a/@href').extract()[0]

        hxsd = get_page(BASE_URL + desc_addr)
        item['description'] = " ".join(hxsd.select('//div[@class="colloqitem"]/p/text()').extract()).strip()

        items.append(item)
    return items


def get_picower_events():
    base_url = "http://picower.mit.edu"
    hxs = get_page(base_url + "/events/calendar/all")
    event_links = hxs.xpath('//div[@class="month-view"]//a/@href').extract()

    items = []

    def text_from_field_name(h, field_name):
        return h.xpath('//text()[contains(., "%s")]/../../following-sibling::div[1]/span/text()' % field_name).extract()[0]


    for event_link in event_links:
        url = base_url + event_link
        h = get_page(url)

        item = {}
        item['url'] = url

        item['title'] = h.xpath('//div[contains(@class, "views-field-field-subtitle-value")]/span/text()').extract()[0]
        item['description'] = h.xpath('//div[contains(@class, "views-field-field-subtitle-second-value")]/span/text()').extract()[0]

        item['datetime_start'] = text_from_field_name(h, "Date + Time")
        item['location'] = text_from_field_name(h, "Location")

        items.append(item)

    return items

def get_CSAIL_events():
    cal = Calendar.from_ical(urlopen("https://calendar.csail.mit.edu/event_calendar.ics").read())
    items = []

    events = [event for event in cal.walk() if 'SUMMARY' in event]

    for event in events:
        try:
            item = {}
            item['title'] = unicode(event['SUMMARY'])
            item['description'] = unicode(event['DESCRIPTION'])
            item['datetime_start'] = event['DTSTART'].dt
            item['datetime_end'] = event['DTEND'].dt
            item['location'] = unicode(event['LOCATION'])
            items.append(item)
            # Is timezone ok? check this
            pass
        except KeyError:
            print "Keyerror in get_CSAIL_EVENTS"

    return items











