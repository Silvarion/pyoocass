from .Database import Database
from .Keyspace import Keyspace

class Table:
    def __init__(self, keyspace: Keyspace, name: str) -> None:
        self.database = keyspace.database
        self.keyspace = keyspace
        self.name = name