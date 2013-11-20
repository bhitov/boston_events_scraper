from lib.scraper import ICalScraper


class HarvardMoSCEventsScraper(ICalScraper):
    scrape_url = "http://hmsc.harvard.edu/calendar/export.ics"