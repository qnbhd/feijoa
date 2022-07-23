from pprint import pformat


class Configuration(dict):

    def __init__(self, *args, requestor='UNKNOWN', **kwargs):
        super().__init__(*args, **kwargs)
        self.requestor = requestor

    def __str__(self):
        fmt = pformat(dict(self.items()))
        return f'Configuration({fmt}, requestor={self.requestor})'

    def __repr__(self):
        return self.__str__()