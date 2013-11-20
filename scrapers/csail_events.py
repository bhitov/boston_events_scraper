from lib.scraper import ICalScraper


class CSAILEventsScraper(ICalScraper):
    scrape_url = "https://calendar.csail.mit.edu/event_calendar.ics"
    additional_fields = ['LOCATION']