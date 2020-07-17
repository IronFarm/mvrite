import datetime
import time

import requests
from lxml import html

from mvrite import get_logger, listing, pipe


class NoMoreResultsException(BaseException):
    """
    Exception thrown when a search results page contains no more valid results
    """
    pass


class DateParseError(BaseException):
    pass


class ResultList:
    headers = {
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/81.0.4044.122 Safari/537.36'
    }

    def __init__(self, location_id, min_bedrooms, max_bedrooms):
        self.location_id = location_id
        self.min_bedrooms = min_bedrooms
        self.max_bedrooms = max_bedrooms

        # Initialise logging
        self.logger = get_logger(type(self).__name__)
        self.logger.info('Search prepared for %s', str(self))

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
            session.headers.update(self.headers)

            while True:
                # Fetch page
                self.logger.info('Retrieving results page %s', page + 1)
                response = session.get(self.url, params=dict(index=24 * page, **self.search_parameters))

                if response.ok:
                    yield response.text
                else:
                    raise requests.HTTPError()

                page += 1
                time.sleep(10)

                if page >= 10:
                    self.logger.error('Aborting after 10 pages')

                    return

    def parse_results(self):
        """
        Go through results pages, parsing property elements until there are no more

        :return:
        """

        result_queue = pipe.ListingQueue()

        for body in self.page_through_results():
            root = html.document_fromstring(body)

            property_elements = root.find_class('l-searchResult')
            self.logger.info('Page has %s result elements', len(property_elements))

            for el in property_elements:
                try:
                    listing = self.get_element_details(el)
                    result_queue.publish_message(listing.serialize())
                except NoMoreResultsException:
                    # Page has no more results so return
                    return
                except DateParseError as e:
                    # Log issue and skip to next element
                    self.logger.exception(e)
                    continue

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
                raise DateParseError('Can\'t parse date from listing status "{}"'.format(' '.join(status_data)))

        return listing.ListingPrototype(id_, status_date, status_keyword)

    def __str__(self):
        return '<Location: {!r}, Min. Bedrooms: {}, Max. Bedrooms: {}>'.format(
            self.location_id, self.min_bedrooms, self.max_bedrooms
        )


def main():
    results = ResultList('OUTCODE^2333', 3, 5)
    results.parse_results()


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    main()
