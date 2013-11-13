from scrapers.scrapers import TuftsEventsScraper, PicowerEventScraper, CSAILEventsScraper

def demo():
    print "Scraping Tufts"
    tufts_events = TuftsEventsScraper().parse()

    print "Scraping Picower"
    picower_events = PicowerEventScraper().parse()

    print "Scraping CSAIL"
    CSAIL_events = CSAILEventsScraper().parse()

    return tufts_events, picower_events, CSAIL_events

