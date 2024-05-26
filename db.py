import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.connection_cursor = self.connection.cursor()
        self.cursor = self.connection_cursor

    async def get_period(self):
        with self.connection:
            return self.cursor.execute("SELECT period FROM data", ).fetchall()[0]

    async def set_period(self, period):
        with self.connection:
            self.cursor.execute("UPDATE data SET period = ?", (period,))

    async def get_stop(self):
        with self.connection:
            return self.cursor.execute("SELECT stop FROM data", ).fetchall()[0]

    async def set_stop(self, pause):
        with self.connection:
            self.cursor.execute("UPDATE data SET stop = ?", (pause,))

    async def get_launched(self):
        with self.connection:
            return self.cursor.execute("SELECT launched FROM data", ).fetchall()[0]

    async def set_launched(self, launched):
        with self.connection:
            self.cursor.execute("UPDATE data SET launched = ?", (launched,))

    async def get_delete(self):
        with self.connection:
            return self.cursor.execute("SELECT del FROM data", ).fetchall()[0]

    async def set_delete(self, delete):
        with self.connection:
            self.cursor.execute("UPDATE data SET del = ?", (delete,))

    async def get_time(self):
        with self.connection:
            return self.cursor.execute("SELECT time FROM data", ).fetchall()[0]

    async def set_time(self, time):
        with self.connection:
            self.cursor.execute("UPDATE data SET time = ?", (time,))
