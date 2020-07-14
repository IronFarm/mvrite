import datetime

import requests
from lxml import html


class ResultList:
    def __init__(self, outcode, n_bedrooms):
        self.outcode = outcode
        self.n_bedrooms = n_bedrooms

    @property
    def url(self):
        return f'https://www.rightmove.co.uk/property-for-sale/{self.outcode}/{self.n_bedrooms}-bed-houses.html'

    def get_html(self):
        response = requests.get(self.url)

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
            if status_data[1] != 'yesterday':
                raise
            else:
                status_date = datetime.date.today() - datetime.timedelta(days=1)

        return id_, status_keyword, status_date


def main():
    results = ResultList('SE6', 3)
    print(results.url)
    results.parse_results()


if __name__ == '__main__':
    main()
