class Events:
    def __init__(self):
        self._listeners = {}

    def listen(self, event, handler):
        if event not in self._listeners:
            self._listeners[event] = []

        self._listeners[event].append(handler)

    def dispatch(self, event, *args):
        if event not in self._listeners:
            raise

        for listener in self._listeners[event]:
            listener(*args)
