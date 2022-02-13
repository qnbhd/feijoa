import datetime

from polytune.models.result import Result


def test_result():
    timestamp = datetime.datetime.now()

    r1 = Result(id=0, timestamp=timestamp,
                metrics={'time': 0.1, 'rate': 0.7}, state='OK')

    r2 = Result(id=1, timestamp=timestamp,
                metrics={'time': 0.2, 'rate': 0.9}, state='OK')
