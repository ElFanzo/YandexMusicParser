from os import remove
from sqlite3 import connect, OperationalError


class DataCtx:
    """Data context class for storing scraped data in the database.

    rowcount
      Count of inserted, changed or deleted records.
    """

    def __init__(self):
        self.rowcount = 0

        self.__conn = connect("cache/YandexMusicData.db")
        self.__cursor = self.__conn.cursor()

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

        if rows:
            self.rowcount = len(rows)

        return rows

    def __del__(self):
        """Close a connection after all operations."""
        self.__conn.close()
