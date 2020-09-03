# coding:utf-8
"""Add an HTTP header to each response."""


class AddHeader:
    def __init__(self):
        self.num = 0

    def response(self, flow):
        self.num = self.num + 1
        flow.response.headers["count"] = str(self.num)
        _names = list(flow.response.headers)
        _values = [flow.response.headers[x] for x in _names]
        _data = {_names[i]:_values[i] for i in range(len(_names))}


        print(_data)


addons = [
    AddHeader()
]