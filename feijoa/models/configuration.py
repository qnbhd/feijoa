from pprint import pformat


class Configuration(dict):
    def __init__(
        self,
        *args,
        requestor="UNKNOWN",
        request_id="UNKNOWN",
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.requestor = requestor
        self.request_id = request_id

    def __str__(self):
        fmt = pformat(dict(self.items()))
        return (
            f"Configuration({fmt}, "
            f"requestor={self.requestor}, "
            f"request_id={self.request_id})"
        )

    def __repr__(self):
        return self.__str__()
