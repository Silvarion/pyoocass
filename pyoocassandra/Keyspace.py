from .Database import Database

class Keyspace:
    
    def __init__(self, database: Database) -> None:
        self.database = database
        pass