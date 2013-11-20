import inspect

import os
from lib.scraper import Scraper


class ScraperLoader(object):
    """
    Scans the ./scrapers/ directory and imports objects into lists based on base class

    Based on code copyright 2005 Jesse Noller <jnoller@gmail.com>
    http://code.activestate.com/recipes/436873-import-modulesdiscover-methods-from-a-directory-na/
    """

    def __init__(self):
        self._classes = {}
        self.load()

    def load(self):
        self._classes = {}
        for f in os.listdir(os.path.join(os.getcwd(), "scrapers")):
            module_name, ext = os.path.splitext(f)
            if ext == ".py":
                module = __import__("scrapers." + module_name, fromlist=['dummy'])
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    bases = inspect.getmro(obj)

                    if obj is Scraper:
                        continue

                    if len(bases) > 1 and Scraper in bases:
                        base = bases[1].__name__.rsplit('.',1)[0]
                        self._classes[name] = obj
                        print("Loaded %s::%s" % (base, obj.__name__))

    def get(self, classname):
        return self._classes.get(classname, [])