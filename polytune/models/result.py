import datetime


class Result:

    idx = 0

    def __init__(self, idx, time):
        self.idx = idx
        self.timestamp = datetime.datetime.now()
        self.time = time

    def __repr__(self):
        return f'Result(id={self.idx},' \
               f' time={self.time},' \
               f' timestamp={self.timestamp})'

    @classmethod
    def get(cls, time):
        instance = cls(cls.idx, time)
        cls.idx += 1
        return instance

    def __lt__(self, other):
        return self.time < other.time
