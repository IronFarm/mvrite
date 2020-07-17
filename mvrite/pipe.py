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
        self.channel.basic_qos(prefetch_count=1)

    def publish_message(self, message: str):
        self.channel.basic_publish(exchange='', routing_key=self._queue_name, body=message)

    def fetch_message(self):
        try:
            message_generator = self.channel.consume(self._queue_name, inactivity_timeout=10)
            return next(message_generator)
        finally:
            self.channel.cancel()

    def acknowledge_message(self, tag):
        self.channel.basic_ack(tag)


def main():
    _ = ListingQueue()


if __name__ == '__main__':
    main()
