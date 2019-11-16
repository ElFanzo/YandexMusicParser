from os import remove
from sqlite3 import connect, OperationalError


class DataCtx:
    """Data context class for storing scraped data in the database.

    rowcount
      Count of inserted, changed or deleted records.
    """

    __conn = connect("cache/YandexMusicData.db")
    __cursor = None

    def __init__(self):
        self.rowcount = 0

        self.__cursor = self.__conn.cursor()

    def execute(self, query: str, *params):
        """Execute SQl scripts.

        :param query: a query string
        :param params: a query parameters
        :return: rowcount
        """
        return self.__exec(True, query, *params)

    def execute_many(self, query: str, *params):
        """Execute SQL scripts with many parameters.

        :param query: a query string
        :param params: a query parameters
        :return: rowcount
        """
        return self.__exec(False, query, *params)

    def __exec(self, is_one: bool, query: str, *params):
        if is_one:
            self.__cursor.execute(query, *params)
        else:
            self.__cursor.executemany(query, *params)
        self.rowcount = self.__cursor.rowcount
        self.__conn.commit()

        return self.rowcount

    def select(self, query: str, *params):
        """Select rows from a table.

        :param query: a query string
        :param params: a query parameters
        :return: a list of selected records
        """
        self.__cursor.execute(query, *params)
        rows = self.__cursor.fetchall()
        self.rowcount = len(rows)

        return rows

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

    def __del__(self):
        """Close a connection after all operations."""
        self.__conn.close()
