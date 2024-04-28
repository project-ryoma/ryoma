# create a class StateStore to store the state of the tool
# the StateState has functionality to store and retrieve the state of the tool
# there are also SqlStateStore that inherits from StateStore
# and also LocalStateStore that inherits from StateStore

from abc import ABC, abstractmethod


class StateStore(ABC):
    @abstractmethod
    def store(self, key, value):
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, key):
        raise NotImplementedError

    @abstractmethod
    def delete(self, key):
        raise NotImplementedError

    @abstractmethod
    def update(self, key, value):
        raise NotImplementedError


class LocalStateStore(StateStore):
    def __init__(self):
        self.states = {}

    def store(self, key, value):
        self.states[key] = value

    def retrieve(self, key):
        return self.states.get(key)

    def delete(self, key):
        if key in self.states:
            del self.states[key]

    def update(self, key, value):
        self.states[key] = value
