class HeaderBag:
    def __init__(self, headers=[]):
        self.headers = headers

    def remove(self, header_name):
        headers = dict(self.headers)

        if (hasattr(headers, header_name)):
            headers.pop(header_name)

        self.headers = headers

    def add(self, header_name, value):
        self.headers.append((header_name.lower(), value))

    def count(self):
        return len(self.headers)

    def has(self, header_name):
        return header_name.lower() in dict(self.headers)

    def get_all(self):
        return self.headers

    def get(self, header_name):
        if self.has(header_name):
            return dict(self.headers).get(header_name.lower())
