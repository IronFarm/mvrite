import datetime
import json
import urllib.parse

import requests
from lxml import html

from mvrite import get_logger, search


class ListingPrototype:
    def __init__(self, id_: int, status_date: datetime.date, status_keyword: str):
        self.id = id_
        self.status_date = status_date
        self.status_keyword = status_keyword

    def __str__(self):
        return '<ID: {}, Status Date: {}, Status Keyword: {!r}>'.format(self.id, self.status_date, self.status_keyword)

    def serialize(self):
        return json.dumps({'id': self.id, 'status_date': str(self.status_date), 'status_keyword': self.status_keyword})

    @classmethod
    def deserialize(cls, body):
        body = json.loads(body)

        return cls(body['id'], datetime.date.fromisoformat(body['status_date']), body['status_keyword'])


class Listing:
    _url_template = 'https://www.rightmove.co.uk/property-for-sale/property-{id}.html'

    logger = get_logger('Listing')

    def __init__(
        self, id_, title, location_string, estate_agent,
        date_added, status_date, status_keyword, price,
        latitude, longitude
    ):
        self.id = id_
        self.title = title
        self.location_string = location_string
        self.estate_agent = estate_agent
        self.date_added = date_added
        self.status_date = status_date
        self.status_keyword = status_keyword
        self.price = price
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def from_prototype(cls, prototype: ListingPrototype):
        response = requests.get(cls._url_template.format(id=prototype.id), headers=search.ResultList.headers)

        root = html.document_fromstring(response.text)
        image_elements = root.findall('.//img')

        # Extract title and location string
        title = root.find('.//title').text
        title, location_string = title.split(' for sale in ')

        # Get estate agent
        estate_agent = root.get_element_by_id('aboutBranchLink').find('strong').text

        # Date added
        try:
            date_added_string = root.get_element_by_id('firstListedDateValue').text
            date_added = datetime.datetime.strptime(date_added_string, '%d %B %Y').date()
        except KeyError:
            cls.logger.warning('No date string found')
            date_added = None

        # Price data
        price_raw = root.get_element_by_id('propertyHeaderPrice').find('strong').text
        price_clean = price_raw.strip().replace('£', '').replace(',', '')
        try:
            price = int(price_clean)
        except ValueError:
            # Unparsable price
            cls.logger.warning('Cannot parse price from string "%s"', price_clean)
            price = None

        # Extract lat & long
        map_src = [el.attrib['src'] for el in image_elements if '/map/' in el.attrib['src']][0]
        parsed = urllib.parse.urlparse(map_src)
        parsed_qs = urllib.parse.parse_qs(parsed.query)

        return cls(
            prototype.id, title, location_string, estate_agent,
            date_added, prototype.status_date, prototype.status_keyword, price,
            float(parsed_qs['latitude'][0]), float(parsed_qs['longitude'][0])
        )


def main():
    prototype = ListingPrototype(94960397, None, None)
    _ = Listing.from_prototype(prototype)


if __name__ == '__main__':
    main()
