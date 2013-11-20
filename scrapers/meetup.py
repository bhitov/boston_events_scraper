import requests

class MeetupEventsScraper:
    """ Gather event data from a given list of Meetup groups

    Attributes:
        groups: list of groups that we want to know about their events
    """
    def __init__(self):
        self.groups = ['API-Craft-Boston',
                       'Boston-Algorithmic-Trading',
                       'Big-Data-Analytics-Discovery-Visualization',
                       'Boston-Data-Mining',
                       'bostonhadoop',
                       'boston-java']
                       #'Boston-Music-Technology-Group',
                       #'Boston_New_Technology',
                       #'bostonphp',
                       #'bostonpython',
                       #'Boston-useR',
                       #'Code-for-Boston',
                       #'Data-Visualization-in-MetroWest-Boston',
                       #'The-Cambridge-Semantic-Web-Meetup-Group',
                       #'The-Data-Scientist',
                       #'The-Happathon-Project-Hacking-Somerville-Happiness']
                       
    def scrape_these_groups(self, key):
        """ Creates urls to use for scraping

        Args:
            key: key from meetup ('http://www.meetup.com/meetup_api/key/')

        Returns:
        A dict mapping keys to the corresponding url created:
        
        {'bostonpython': 'https://api.meetup.com/2/events?'\
                                       + 'key=#get_your_own_key'\
                                       + '&group_urlname=bostonpython'\
                                       + '&page=20'}
        """
        meetup_dict = {}
        for group in self.groups:
            meetup_dict[group] = 'https://api.meetup.com/2/events?' \
            + 'key=' + key \
            + '&group_urlname=' + group + '&page=20'
        return meetup_dict
            
    def parse_events_json(self, key):
        """ Parse events data from json

        The following options are available:
            status
            utc_offset
            event_url
            group
            description
            created
            rsvp_limit
            venue
            updated
            visibility
            yes_rsvp_count
            time
            waitlist_count
            headcount
            maybe_rsvp_count
            id
            name
        Args:
            key: key from meetup ('http://www.meetup.com/meetup_api/key/')
        Returns:
            A dict mapping keys to the corresponding list of tuples where
            each tuple is an event that includes information in this order:
            (title, date since epoch, location, description, waitlist count)
        """
        group_events = {}
        for group in self.scrape_these_groups(key):
            r = requests.get(self.scrape_these_groups(key)[group])
            event_list = []
            for event in r.json()['results']:
                event_list.append( \
                (event['name'], # title
                 event['time'], # datetime_start, datetime_end
                 event['venue'], # location
                 event['description'], # description
                 event['waitlist_count']) # waitlist_count
                )
            group_events[group] = event_list
        return group_events
