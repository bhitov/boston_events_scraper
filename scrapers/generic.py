__author__ = 'ben'


from urllib2 import urlopen
from scrapy.selector import HtmlXPathSelector
from icalendar import Calendar


class Scraper(object):

    def new_event(self):
        '''
        Populate events with metadata
        '''
        meta_fields = ['scrape_url', 'subject']

        event = {}
        for field in meta_fields:
            if hasattr(self, field):
                event[field] = getattr(self, field)
        return event

    def parse(self):
        '''
        Do the things! Should return a list of events.
        '''
        raise NotImplementedError


class ICalScraper(Scraper):
    '''
    Parses an Ical file
    '''
    scrape_url = None


    def parse(self):
        cal = Calendar.from_ical(urlopen(self.scrape_url).read())
        items = []
        cal_events = self.filter_cal(cal)

        events = []
        for cal_event in cal_events:
            event = self.parse_cal_event(cal_event)
            if event is not None:
                events.append(event)
        return events

    def filter_cal(self, cal):
        '''
        filter out ical items that do not represent events
        '''
        cal_events = [cal_event for cal_event in cal.walk() if 'DTSTART' in cal_event]
        return cal_events

    def parse_cal_event(self, cal_event):
        '''
        Convert ical events to dicts
        '''
        try:
            event = {}
            event['title'] = unicode(cal_event['SUMMARY'])
            event['description'] = unicode(cal_event['DESCRIPTION'])
            event['datetime_start'] = cal_event['DTSTART'].dt
            event['datetime_end'] = cal_event['DTEND'].dt
            event['location'] = unicode(cal_event['LOCATION'])
            event['scrape_url'] = self.scrape_url
            return event
            # Is timezone ok? check this
        except KeyError:
            print "Keyerror in ical parser for %s" % self.scrape_url


#def get_page(url):
#    '''
#    Returns an xpath selector for a url
#    '''
#    html = urlopen(url).read()
#    return HtmlXPathSelector(text=html)
#

class HtmlScraper(Scraper):
    '''
    Scraper for html pages containing a list of events
    '''
    scrape_url = None

    @classmethod
    def get_page(cls, url=None):
        '''
        Returns an xpath node for a url
        '''
        if url is None:
            url = cls.scrape_url
        html = urlopen(url).read()
        return HtmlXPathSelector(text=html)

    def parse(self):
        xp = self.get_page()
        event_html_list_xp = self.get_event_html_list(xp)

        events = []
        for exp in event_html_list_xp:
            event = self.new_event()
            events.append(self.parse_event_html(exp, event))

        return events

    def get_event_html_list(self, xp):
        '''
        Takes an xpath node and returns an iterable of xpath nodes or links
        '''
        raise NotImplementedError

    def parse_event_html(self, xp, event):
        '''
        Parses an xpath node or link, returns an event
        '''
        raise NotImplementedError









