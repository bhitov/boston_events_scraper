from datetime import datetime, timedelta

from suds.client import Client
from suds.xsd.doctor import ImportDoctor, Import

from generic import HtmlScraper, ICalScraper, Scraper

import arrow

class MITMainEventsScraper(Scraper):
    '''
    Use the MIT SOAP interface to pull public lectures

    This is a PITA, maybe try a different approach?
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

        # This data isn't useful yet, just a demo
        data = client.service.getDateRangeEvents(start_date.strftime(fstr), end_date.strftime(fstr))

        # We want to build a list of SearchCriterion but gah fuck SOAP
        # It will look something like:
        client.factory.create('SearchCriterion')
        # and then somehow it works or something


        return data



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
