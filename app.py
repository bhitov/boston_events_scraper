#from scrapers.scrapers import TuftsEventsScraper, PicowerEventScraper, CSAILEventsScraper
from scraper_loader import ScraperLoader

def demo():
    loader = ScraperLoader()

    print "Scraping Tufts"
    tufts_events = loader.get("TuftsEventsScraper")().parse()

    print "Scraping Picower"
    picower_events = loader.get("PicowerEventScraper")().parse()

    print "Scraping CSAIL"
    CSAIL_events = loader.get("CSAILEventsScraper")().parse()

    return tufts_events, picower_events, CSAIL_events

if __name__ == "__main__":
    demo()