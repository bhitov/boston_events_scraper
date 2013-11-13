from datetime import datetime, timedelta

from suds.client import Client
from suds.xsd.doctor import ImportDoctor, Import

from generic import HtmlScraper, ICalScraper, Scraper

import arrow


def parse_soap_date(soap_date):
    data = {}
    for field in ['year', 'day', 'hour', 'minute', 'month']:
        data[field] = int(getattr(soap_date, field)[0])
    return datetime(**data)

class MITMainEventsScraper(Scraper):
    '''
    Use the MIT SOAP interface to pull public lectures
    '''
    scrape_url = "http://events.mit.edu/MITEventsFull.wsdl"

    def parse(self):
        imp = Import("http://schemas.xmlsoap.org/soap/encoding/")
        imp.filter.add("http://events.mit.edu/MIT/Events/")
        doctor = ImportDoctor(imp)
        client = Client(self.scrape_url, doctor=doctor)

        start_date = datetime.now().date()
        end_date = (start_date + timedelta(days=4))
        fstr = "%Y/%m/%d"

        start_date = start_date.strftime(fstr)
        end_date = end_date.strftime(fstr)

        def make_criteria(criteria_dict):
            search_criterion = []
            for field in criteria_dict:
                value = criteria_dict[field]
                if type(value) is not type([]):
                    value = [value]
                criterion = client.factory.create('SearchCriterion')
                criterion.field = field
                criterion.value = value
                search_criterion.append(criterion)
            return search_criterion

        # Couldn't get category filtering to work, must do it in post processing
        criteria_dict = {
            'start' : start_date,
            'end' : end_date,
            'opento' : '1', # public
        }

        soap_events = client.service.findEvents(make_criteria(criteria_dict))

        events = []

        def safe_getattr(sp, attr):
            spa = getattr(sp, attr)
            if len(spa) > 0:
                return spa[0]

        def parse_categories(cats):
            category_ids = []
            category_names = []
            for cat in cats:
                category_ids.append(int(safe_getattr(cat, 'catid')))
                category_names.append(safe_getattr(cat, 'name'))
            return category_ids, category_names

        for soap_event in soap_events:
            event = self.new_event()
            event['datetime_start'] = parse_soap_date(soap_event.start[0])
            event['datetime_end'] = parse_soap_date(soap_event.end[0])

            event['location'] = safe_getattr(soap_event, 'location')
            event['description'] = safe_getattr(soap_event, 'description')
            event['title'] = safe_getattr(soap_event, 'title')
            event['opento'] = safe_getattr(soap_event, 'opento')
            event['category_ids'], event['category_names'] = parse_categories(safe_getattr(soap_event, 'categories'))
            events.append(event)

        def category_filter(event):
            # 2 is the category id for lectures
            return 2 in event['category_ids']

        return filter(category_filter, events)


class TuftsEventsScraper(HtmlScraper):
    scrape_url = 'http://www.ece.tufts.edu/research/colloquia/current.php'

    def parse_date_string(self, date, time):
        '''
        Convert ex. November 9, 1999 to datetime
        '''
        d = arrow.get(date, "MMMM D, YYYY").date()

        # The "H:mm a" seems to work even though arrow docs suggest it shouldn't
        ts, te = [arrow.get(time_string.strip(), "H:mm a").time() for time_string in time.split('-')]
        return datetime.combine(d, ts), datetime.combine(d, te)

    def get_event_html_list(self, xp):
        return xp.xpath('//div[@class="colloqitem"]/div[@class="row"]')

    def parse_event_html(self, xp, event):
        BASE_URL = "http://www.ece.tufts.edu"

        dl_section, desc_section = xp.xpath('div')
        time_section = dl_section.xpath('div[@class="colloqdate"]/text()').extract()

        event['datetime_start'], event['datetime_end'] = self.parse_date_string(*time_section)

        event['location'] = dl_section.xpath('div[@class="colloqplace"]/text()').extract()[0]
        event['title'] = desc_section.xpath('div[@class="colloqtitle"]/a/text()').extract()[0]
        desc_addr = desc_section.xpath('div[@class="colloqtitle"]/a/@href').extract()[0]

        hxsd = self.get_page(BASE_URL + desc_addr)
        event['description'] = " ".join(hxsd.xpath('//div[@class="colloqevent"]/p/text()').extract()).strip()

        return event


class PicowerEventScraper(HtmlScraper):
    base_url = "http://picower.mit.edu"
    scrape_url = base_url + "/events/calendar/all"

    def text_from_field_name(self, h, field_name):
        '''
        Because of disgusting formatting on the picower page:
            - search for a string that we know is labeling a field
            - find the next div after that, which will contain the field
        '''
        return h.xpath('//text()[contains(., "%s")]/../../following-sibling::div[1]/span/text()' % field_name).extract()[0]

    def get_event_html_list(self, xp):
        return xp.xpath('//div[@class="month-view"]//a/@href').extract()

    def parse_event_html(self, xp, event):
        url = self.base_url + xp
        h = self.get_page(url)
        event['event_url'] = url

        event['title'] = h.xpath('//div[contains(@class, "views-field-field-subtitle-value")]/span/text()').extract()[0]
        event['description'] = h.xpath('//div[contains(@class, "views-field-field-subtitle-second-value")]/span/text()').extract()[0]

        event['datetime_start'] = self.text_from_field_name(h, "Date + Time")
        event['location'] = self.text_from_field_name(h, "Location")
        return event

class CSAILEventsScraper(ICalScraper):
    scrape_url = "https://calendar.csail.mit.edu/event_calendar.ics"
    additional_fields = ['LOCATION']

class HarvardMoSCEventsScraper(ICalScraper):
    scrape_url = "http://hmsc.harvard.edu/calendar/export.ics"

class HMSEventsScraper(ICalScraper):
    #This will need heavy filtering to not be annoying
    scrape_url = "http://www.trumba.com/calendars/harvardmedicalschool.ics"
    additional_fields = ['LOCATION', ['URL', 'event_url']]
