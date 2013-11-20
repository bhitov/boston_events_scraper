from lib.scraper import ICalScraper


class HMSEventsScraper(ICalScraper):
    #This will need heavy filtering to not be annoying
    scrape_url = "http://www.trumba.com/calendars/harvardmedicalschool.ics"
    additional_fields = ['LOCATION', ['URL', 'event_url']]