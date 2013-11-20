from scraper_loader import ScraperLoader
from lib.test import ScraperTestMakerMixin, ScraperTestRunnerMixin


def demo():
    loader = ScraperLoader()

    events = {}

    for scraper in loader.get_all().itervalues():
        if scraper.skip:
            continue
        print "Scraping %s" % scraper
        events[scraper.__name__] = scraper().parse()

    return events

# These test functions mess with the namespace,
# don't run them and other code from the same instance
def make_tests():
    loader = ScraperLoader()
    for scraper in loader.get_all().itervalues():
        if scraper.skip:
            continue
        print "Making test for %s" % scraper
        try:
            scraper.__bases__ += (ScraperTestMakerMixin, )
            scraper().make_test()
        except Exception, e:
            print(e)

def run_tests():
    loader = ScraperLoader()
    results = {}

    for scraper in loader.get_all().itervalues():
        if scraper.skip:
            continue
        print "Running test for %s" % scraper
        scraper.__bases__ += (ScraperTestRunnerMixin, )
        s = scraper()
        if s.has_test():
            results[scraper.__name__] = s.run_test()[0]

    return results


if __name__ == "__main__":
    returns = demo()
    print returns