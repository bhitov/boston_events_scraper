from lib.scraper import HtmlScraper


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