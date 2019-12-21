from sqlite3 import connect


class DataCtx:
    """Data context class for storing scraped data in the database."""

    def __init__(self):
        self.__conn = connect("yandex_music/cache/YandexMusicData.db")
        self.__cursor = self.__conn.cursor()

    def execute(self, query: str, *params):
        """Execute SQl scripts.

        :param query: a query string
        :param params: a query parameters
        """
        return self.__exec(query, *params)

    def execute_many(self, query: str, *params):
        """Execute SQL scripts with many parameters.

        :param query: a query string
        :param params: a query parameters
        """
        return self.__exec(query, *params, is_many=True)

    def execute_script(self, script: str):
        """Execute all SQL scripts by one query.

        :param script: a string with queries
        """
        self.__cursor.executescript(script)
        self.__conn.commit()

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

    def __exec(self, query: str, *params, is_many: bool = False):
        if is_many:
            self.__cursor.executemany(query, *params)
        else:
            self.__cursor.execute(query, *params)

        self.__conn.commit()

    def __select(self, query: str, *params, is_all: bool = False):
        self.__cursor.execute(query, *params)
        if is_all:
            rows = self.__cursor.fetchall()
        else:
            rows = self.__cursor.fetchone()

        return rows

    def __del__(self):
        """Close a connection after all operations."""
        self.__conn.close()
