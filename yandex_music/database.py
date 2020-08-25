from sqlite3 import connect


class DataCtx:
    """Data context class for storing scraped data in the database."""

    def __init__(self):
        self._conn = connect("yandex_music/cache/YandexMusicData.db")
        self._cursor = self._conn.cursor()

    def execute(self, query: str, *params):
        """Execute SQl scripts.

        :param query: a query string
        :param params: a query parameters
        """
        return self._exec(query, *params)

    def execute_many(self, query: str, *params):
        """Execute SQL scripts with many parameters.

        :param query: a query string
        :param params: a query parameters
        """
        return self._exec(query, *params, is_many=True)

    def execute_script(self, script: str):
        """Execute all SQL scripts by one query.

        :param script: a string with queries
        """
        self._cursor.executescript(script)
        self._conn.commit()

    def select(self, query: str, *params):
        """Select rows from a table.

        :param query: a query string
        :param params: a query parameters
        :return: a list of selected records
        """
        return self._select(query, *params)

    def select_all(self, query: str, *params):
        """Select rows from a table.

        :param query: a query string
        :param params: a query parameters
        :return: a list of selected records
        """
        return self._select(query, *params, is_all=True)

    def _exec(self, query: str, *params, is_many: bool = False):
        if is_many:
            self._cursor.executemany(query, *params)
        else:
            self._cursor.execute(query, *params)

        self._conn.commit()

    def _select(self, query: str, *params, is_all: bool = False):
        self._cursor.execute(query, *params)
        if is_all:
            rows = self._cursor.fetchall()
        else:
            rows = self._cursor.fetchone()

        return rows

    def __del__(self):
        """Close a connection after all operations."""
        self._conn.close()
