"""
Retrieve messages from the processing queue then scrape their details and add them to the history DB if required
"""
import mariadb

from mvrite import config, get_logger, listing, queue

logger = get_logger(__name__)


def get_connection():
    return mariadb.connect(**config['DB'])


def scrape_listing_and_log(prototype: listing.ListingPrototype):
    logger.info('Scraping listing data')
    fl = listing.Listing.from_prototype(prototype)

    logger.info('Logging listing data to DB')
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO listings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', (
                fl.id, fl.title, fl.location_string, fl.estate_agent,
                fl.date_added, fl.status_date, fl.status_keyword, fl.price,
                fl.latitude, fl.longitude
            )
        )


def main():
    logger.info('Fetching message from queue')

    result_queue = queue.ListingQueue()
    method, _, message = result_queue.fetch_message()

    logger.info('Received message "%s"', message)
    if message is None:
        logger.info('Empty message, no new data available')
        return

    logger.info('Deserializing message')
    listing_proto = listing.ListingPrototype.deserialize(message)
    logger.info('Deserialized message "%s"', listing_proto)

    logger.info('Checking whether listing present in history table')
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT 1 FROM listings '
            'WHERE id = ? '
            '  AND status_date = ? '
            '  AND status_keyword = ?;',
            (listing_proto.id, listing_proto.status_date, listing_proto.status_keyword)
        )

        results = list(cursor)

    if not results:
        logger.info('Listing not in history table')
        try:
            scrape_listing_and_log(listing_proto)
        except Exception:
            logger.exception('Failed to log result to DB')
    else:
        logger.info('Listing in history table')

    result_queue.acknowledge_message(method.delivery_tag)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    main()
