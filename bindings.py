class BoolState:
    def __init__(self, value=False):
        self.value = value
        self.listeners = []

    def set(self, value):
        if self.value == value:
            return
        self.value = value
        for cb in self.listeners:
            cb(value)

    def bind(self, callback, invert=False):
        if invert:
            self.listeners.append(lambda v: callback(not v))
            callback(not self.value)
        else:
            self.listeners.append(callback)
            callback(self.value)