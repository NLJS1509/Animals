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

    async def get_sleep(self):
        with self.connection:
            return self.cursor.execute("SELECT time_to_sleep FROM data", ).fetchall()[0]

    async def set_sleep(self, time):
        with self.connection:
            self.cursor.execute("UPDATE data SET time_to_sleep = ?", (time,))

    async def get_up(self):
        with self.connection:
            return self.cursor.execute("SELECT time_to_up FROM data", ).fetchall()[0]

    async def set_up(self, time):
        with self.connection:
            self.cursor.execute("UPDATE data SET time_to_up = ?", (time,))

    async def get_wl(self):
        with self.connection:
            return self.cursor.execute("SELECT white_list FROM data", ).fetchall()

    async def set_wl(self, wl):
        with self.connection:
            self.cursor.execute("INSERT INTO 'data' ('white_list') VALUES (?)", (wl,))

    async def del_wl(self, wl):
        with self.connection:
            self.cursor.execute(f"DELETE FROM data WHERE white_list LIKE '%{wl}%'")

    async def get_start(self):
        with self.connection:
            return self.cursor.execute("SELECT time_to_start FROM data", ).fetchall()

    async def set_start(self, start):
        with self.connection:
            self.cursor.execute("INSERT INTO 'data' ('time_to_start') VALUES (?)", (start,))