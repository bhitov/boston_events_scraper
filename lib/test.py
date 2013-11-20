from urllib import urlopen
import datetime
import pickle
import os
import json

import httpretty

class ScraperTestMakerMixin(object):
    def testmaker_url_get(self, url):
        data = urlopen(url).read()
        self.mock_http_data[url] = data
        return data

    def make_test(self):
        '''
        Stores results of all http requests and the results of parse
        '''
        if not self.mockable:
            raise NotImplementedError
        self.url_get = self.testmaker_url_get
        self.mock_http_data = {}
        results = self.parse()

        test_data = {
            'created_at' :datetime.datetime.now(),
            'url_data' : self.mock_http_data,
            'results' : results
        }

        with open('tests/%s.dat' % self.__class__.__name__, 'wb') as jsonfile:
            pickle.dump(test_data, jsonfile)

    def make_mocks(self):
        self.mock_http_data = {}
        data = self.parse()
        with open('tests/%s.json' % self.__class__.__name__, 'wb') as jsonfile:
            json.dump(self.mock_http_data, jsonfile)
        return data

class ScraperTestRunnerMixin(object):

    def has_test(self):
        test_filepath = 'tests/%s.dat' % self.__class__.__name__
        return os.path.isfile(test_filepath)

    def run_test(self):
        '''
        Mocks http responses and compares parse() results to expected
        values. A 'False' results does not necessarily mean the code is wrong,
        just that results did not match exactly

        '''
        json_filepath = 'tests/%s.dat' % self.__class__.__name__
        if os.path.isfile(json_filepath):
            with open(json_filepath, 'rb') as json_file:
                test_data = pickle.load(json_file)
                httpretty.enable()
                url_data = test_data['url_data']
                for url in url_data:
                    httpretty.register_uri(httpretty.GET,
                                           url,
                                           body = url_data[url])
                results = self.parse()

                httpretty.disable()
                httpretty.reset()
                sort_key = lambda event: event['title']
                results.sort(key=sort_key)
                expected_results = sorted(test_data['results'], key=sort_key)

                same = False
                if len(results) == len(expected_results):
                    same = True
                    for result, expected in zip(results, expected_results):
                        same = same and result == expected

                return same, results, expected_results
