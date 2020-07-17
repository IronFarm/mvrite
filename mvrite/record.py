"""
Retrieve messages from the processing queue then scrape their details and add them to the history DB if required
"""
from mvrite import listing, queue


def main():
    result_queue = queue.ListingQueue()
    method, _, message = result_queue.fetch_message()

    print(message)
    if message is None:
        return

    listing_proto = listing.ListingPrototype.deserialize(message)
    print(listing_proto)

    result_queue.acknowledge_message(method.delivery_tag)


if __name__ == '__main__':
    main()
