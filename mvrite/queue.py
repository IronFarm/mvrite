import pika


class ListingQueue:
    """
    Wrapper class which manages the RabbitMQ queue of listings which require processing
    """

    _queue_name = 'listing_process_queue'

    def __init__(self):
        self.connection = pika.BlockingConnection()
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self._queue_name)

    def publish_message(self, message: str):
        self.channel.basic_publish(exchange='', routing_key=self._queue_name, body=message)


def main():
    queue = ListingQueue()


if __name__ == '__main__':
    main()
