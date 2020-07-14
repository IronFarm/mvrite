import datetime

import requests
from lxml import html


class ResultList:
    def __init__(self, location_id, min_bedrooms, max_bedrooms):
        self.location_id = location_id
        self.min_bedrooms = min_bedrooms
        self.max_bedrooms = max_bedrooms

    @property
    def search_parameters(self):
        return {
            'locationIdentifier': self.location_id,
            'minBedrooms': str(self.min_bedrooms),
            'maxBedrooms': str(self.max_bedrooms),
            'sortType': '6',
            'propertyTypes': 'detached,semi-detached,terraced',
            'primaryDisplayPropertyType': 'houses'
        }

    @property
    def url(self):
        return f'https://www.rightmove.co.uk/property-for-sale/find.html'

    def get_html(self):
        # Fetch page one
        response = requests.get(self.url, self.search_parameters)

        if response.ok:
            return response.text
        else:
            raise requests.HTTPError()

    def parse_results(self):
        body = self.get_html()
        root = html.document_fromstring(body)

        for el in root.find_class('l-searchResult'):
            print(self.get_element_details(el))

        return

    def get_element_details(self, el):
        # Get ID
        id_ = int(el.attrib['id'].replace('property-', ''))

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
    print(results.url)
    results.parse_results()


if __name__ == '__main__':
    main()
