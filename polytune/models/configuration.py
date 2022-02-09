import hashlib

from polytune.search.space import SearchSpace


class Configuration:

    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return f'Configuration({str(self.data)[1:-1]})'

    def get_hash(self):
        curve = hashlib.sha256()

        for p, v in self.data.items():
            encoded = f'{p}{v}'.encode()
            curve.update(encoded)

        return curve.hexdigest()

    def validate(self):
        pass

    def normalize(self):
        pass

    def render(self, space: SearchSpace, renderer_cls):
        renderer = renderer_cls(self)

        rendered = []
        for p_name in self.data.keys():
            p = space.get_by_name(p_name)
            result = p.accept(renderer)
            rendered.append(result)

        return ' '.join(rendered)
