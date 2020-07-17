import datetime
import json


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
