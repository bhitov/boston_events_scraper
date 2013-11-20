from lib.scraper import ICalScraper


class HarvardMoSCEventsScraper(ICalScraper):
    skip = True
    scrape_url = "http://hmsc.harvard.edu/calendar/export.ics"