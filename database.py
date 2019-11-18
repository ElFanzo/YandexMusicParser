from os import remove
from sqlite3 import connect, OperationalError


class DataCtx:
    """Data context class for storing scraped data in the database.

    rowcount
      Count of inserted, changed or deleted records.
    """

    __conn = connect("cache/YandexMusicData.db")

    def __init__(self):
        self.rowcount = 0

        self.__cursor = self.__conn.cursor()

        self.__create_tables()

    def execute(self, query: str, *params):
        """Execute SQl scripts.

        :param query: a query string
        :param params: a query parameters
        :return: rowcount
        """
        return self.__exec(query, *params)

    def execute_many(self, query: str, *params):
        """Execute SQL scripts with many parameters.

        :param query: a query string
        :param params: a query parameters
        :return: rowcount
        """
        return self.__exec(query, *params, is_many=True)

    def select(self, query: str, *params):
        """Select rows from a table.

        :param query: a query string
        :param params: a query parameters
        :return: a list of selected records
        """
        return self.__select(query, *params)

    def select_all(self, query: str, *params):
        """Select rows from a table.

        :param query: a query string
        :param params: a query parameters
        :return: a list of selected records
        """
        return self.__select(query, *params, is_all=True)

    def save_to_file(self, path: str):
        """Save all data from the Teachers table to a file.

        :param path: the path to a file
        """
        try:
            with open(path, "w", encoding="utf-8") as out:
                for row in self.select("select * from table"):
                    out.write("|".join([str(i) for i in row]) + "\n")
        except OperationalError:
            remove(path)
            print(
                "There is no table in the database yet! "
                "Try again after creating the table."
            )
        else:
            print("All data has been successfully saved to the file.")

    def __exec(self, query: str, *params, is_many: bool = False):
        if is_many:
            self.__cursor.executemany(query, *params)
        else:
            self.__cursor.execute(query, *params)
        self.rowcount = self.__cursor.rowcount
        self.__conn.commit()

        return self.rowcount

    def __select(self, query: str, *params, is_all: bool = False):
        self.__cursor.execute(query, *params)
        if is_all:
            rows = self.__cursor.fetchall()
        else:
            rows = self.__cursor.fetchone()
        self.rowcount = len(rows)

        return rows

    def __create_tables(self):
        self.__cursor.executescript(
            """PRAGMA foreign_keys=on;

            create table if not exists user (
                id integer primary key,
                login text unique not null,
                name text not null
                playlists_count integer);

            create table if not exists playlist (
                user_id integer,
                id integer primary key,
                title text not null,
                tracks_count integer,
                duration integer,
                modified text,
                foreign key (user_id) references user(id) on delete cascade);

            create table if not exists track (
                id integer primary key,
                title text not null,
                year integer not null,
                genre text,
                duration integer);

            create table if not exists artist (
                id integer primary key,
                name text not null,
                likes integer);

            create table if not exists playlist_track (
                user_id integer,
                playlist_id integer,
                track_id integer,
                foreign key (user_id) references user(id) on delete cascade,
                foreign key (playlist_id) references playlist(id) on delete cascade,
                foreign key (track_id) references track(id) on delete cascade);

            create table if not exists artist_track (
                artist_id integer,
                track_id integer,
                foreign key (artist_id) references artist(id) on delete cascade,
                foreign key (track_id) references track(id) on delete cascade);
            """
        )

    def __del__(self):
        """Close a connection after all operations."""
        self.__conn.close()
