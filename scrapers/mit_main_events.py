from datetime import datetime, timedelta

from suds.client import Client
from suds.xsd.doctor import Import, ImportDoctor

from lib.scraper import Scraper
from lib.utils import parse_soap_date


class MITMainEventsScraper(Scraper):
    '''
    Use the MIT SOAP interface to pull public lectures
    '''
    skip = True
    scrape_url = "http://events.mit.edu/MITEventsFull.wsdl"

    def parse(self):
        imp = Import("http://schemas.xmlsoap.org/soap/encoding/")
        imp.filter.add("http://events.mit.edu/MIT/Events/")
        doctor = ImportDoctor(imp)
        client = Client(self.scrape_url, doctor=doctor)

        start_date = datetime.now().date()
        end_date = (start_date + timedelta(days=4))
        fstr = "%Y/%m/%d"

        start_date = start_date.strftime(fstr)
        end_date = end_date.strftime(fstr)

        def make_criteria(criteria_dict):
            search_criterion = []
            for field in criteria_dict:
                value = criteria_dict[field]
                if type(value) is not type([]):
                    value = [value]
                criterion = client.factory.create('SearchCriterion')
                criterion.field = field
                criterion.value = value
                search_criterion.append(criterion)
            return search_criterion

        # Couldn't get category filtering to work, must do it in post processing
        criteria_dict = {
            'start' : start_date,
            'end' : end_date,
            'opento' : '1', # public
        }

        soap_events = client.service.findEvents(make_criteria(criteria_dict))

        events = []

        def safe_getattr(sp, attr):
            spa = getattr(sp, attr)
            if len(spa) > 0:
                return spa[0]

        def parse_categories(cats):
            category_ids = []
            category_names = []
            for cat in cats:
                category_ids.append(int(safe_getattr(cat, 'catid')))
                category_names.append(safe_getattr(cat, 'name'))
            return category_ids, category_names

        for soap_event in soap_events:
            event = self.new_event()
            event['datetime_start'] = parse_soap_date(soap_event.start[0])
            event['datetime_end'] = parse_soap_date(soap_event.end[0])

            event['location'] = safe_getattr(soap_event, 'location')
            event['description'] = safe_getattr(soap_event, 'description')
            event['title'] = safe_getattr(soap_event, 'title')
            event['opento'] = safe_getattr(soap_event, 'opento')
            event['category_ids'], event['category_names'] = parse_categories(safe_getattr(soap_event, 'categories'))
            events.append(event)

        def category_filter(event):
            # 2 is the category id for lectures
            return 2 in event['category_ids']

        return filter(category_filter, events)