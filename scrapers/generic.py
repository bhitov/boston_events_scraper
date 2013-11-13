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

    Fields can be customized like so:

    To toggle on a common field pattern, add the iCal field name
      to additional_fields

      ex. additional_fields = ['LOCATION']

    To add a new iCal to event field map, add either a list with
      [ICAL_FIELD, EVENT_FIELD]
      or a dict with
      {ICAL_FIELD1 : EVENT_FIELD1, ICAL_FIELD2 : EVENT_FIELD2}

      ex. additional_fields = ['CATEGORIES', 'topics']
          additional_fields = {'CATEGORIES' : 'topics'}

    '''
    scrape_url = None
    UNICODE_FIELDS = {
        'SUMMARY': 'title',
        'DESCRIPTION' : 'description',
        'LOCATION' : 'location',
    }
    fields = ['SUMMARY', 'DESCRIPTION']
    additional_fields = []


    def __init__(self):
        '''
        Parses additional_fields
        '''

        self.all_fields = self.fields
        self.cal_to_event_map = dict(self.UNICODE_FIELDS.items())

        for field in self.additional_fields:
            if type(field) == type([]):
                self.cal_to_event_map[field[0]] = field[1]
                self.all_fields.append(field[0])
            elif type(field) == type({}):
                self.cal_to_event_map.update(field)
                self.all_fields += field.keys()
            else:
                self.all_fields.append(field)

    def parse(self):
        cal = Calendar.from_ical(urlopen(self.scrape_url).read())
        self.cal = cal
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

    def parse_cal_event_extra(self, cal_event, event):
        return event

    def parse_cal_event(self, cal_event):
        '''
        Convert ical events to dicts
        '''

        try:
            event = {}
            event['datetime_start'] = cal_event['DTSTART'].dt
            event['datetime_end'] = cal_event['DTEND'].dt
            event['scrape_url'] = self.scrape_url
            for field in self.all_fields:
                try:
                    event[self.cal_to_event_map[field]] = unicode(cal_event[field])
                except KeyError, e:
                    print str(e)
            return event
            # TODO: Is timezone ok? check this
        except KeyError, e:
            print "Date error in ical parser for %s, fatal" % self.scrape_url

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









