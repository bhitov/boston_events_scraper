from scraper_loader import ScraperLoader


def demo():
    loader = ScraperLoader()

    events = {}

    for scraper in loader.get_all().itervalues():
        if scraper.skip:
            continue
        print "Scraping %s" % scraper
        events[scraper.__name__] = scraper().parse()

    return events

if __name__ == "__main__":
    returns = demo()
    print returns