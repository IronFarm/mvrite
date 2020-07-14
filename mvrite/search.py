import datetime
import time

import requests
from lxml import html


class NoMoreResultsException(BaseException):
    pass


class ResultList:
    def __init__(self, location_id, min_bedrooms, max_bedrooms):
        self.location_id = location_id
        self.min_bedrooms = min_bedrooms
        self.max_bedrooms = max_bedrooms

    @property
    def search_parameters(self):
        return {
            'locationIdentifier': self.location_id,
            'minBedrooms': self.min_bedrooms,
            'maxBedrooms': self.max_bedrooms,
            'sortType': 6,
            'propertyTypes': 'detached,semi-detached,terraced',
            'primaryDisplayPropertyType': 'houses'
        }

    @property
    def url(self):
        return f'https://www.rightmove.co.uk/property-for-sale/find.html'

    def page_through_results(self):
        """
        Yields search results HTML page by page

        :return:
        """

        page = 0

        with requests.Session() as session:
            while True:
                # Fetch page
                response = session.get(self.url, params=dict(index=24 * page, **self.search_parameters))

                if response.ok:
                    yield response.text
                else:
                    raise requests.HTTPError()

                page += 1
                time.sleep(10)

                if page >= 10:
                    raise ValueError('Too many pages')

    def parse_results(self):
        """
        Go through results pages, parsing property elements until there are no more

        :return:
        """

        for body in self.page_through_results():
            root = html.document_fromstring(body)

            for el in root.find_class('l-searchResult'):
                try:
                    print(self.get_element_details(el))
                except NoMoreResultsException:
                    return

    def get_element_details(self, el):
        """
        Extract the ID and update information from a property element

        :param el:
        :return:
        """

        # Get ID
        id_ = int(el.attrib['id'].replace('property-', ''))

        if id_ == 0:
            raise NoMoreResultsException()

        # Get latest status
        status_data = el.find_class('propertyCard-branchSummary-addedOrReduced')[0].text.split()
        status_keyword = status_data[0]

        try:
            status_date = status_data[2]
            status_date = datetime.datetime.strptime(status_date, '%d/%m/%Y').date()
        except IndexError:
            if status_data[1] == 'today':
                status_date = datetime.date.today()
            elif status_data[1] == 'yesterday':
                status_date = datetime.date.today() - datetime.timedelta(days=1)
            else:
                raise ValueError('Can\'t parse time from listing status "{}"'.format(' '.join(status_data)))

        return id_, status_keyword, status_date


def main():
    results = ResultList('OUTCODE^2333', 3, 5)
    results.parse_results()


if __name__ == '__main__':
    main()
