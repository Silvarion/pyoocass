from .Database import Database

class Keyspace:
    
    def __init__(self, database: Database) -> None:
        self.database = database
        pass

    def create(self):
        pass

    def drop(self):
        pass

    def get_tables(self):
        pass
    