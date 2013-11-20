import arrow
from datetime import datetime

from lib.scraper import HtmlScraper


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