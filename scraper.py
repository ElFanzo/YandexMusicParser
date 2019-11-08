from grab.error import GrabConnectionError

from json_data import Data
from models import Playlist

ERR_MSG = ("Internet is not available. Please, check your connection "
           "and try again.")


class Listener:
    """The class for scraping data from the Yandex Music site.

    It works only with public accounts.

    :param login: the Yandex Music account's login
    :param playlist: resulting data in the Playlist object
    """

    def __init__(self, login: str):
        self.__login = login
        try:
            self.__data = Data(self.__login)
        except GrabConnectionError:
            print(ERR_MSG)
        else:
            self.playlist = Playlist(self.__data.json)

    def update(self):
        """Update the locally cached JSON file."""
        try:
            self.__data.update()
        except GrabConnectionError:
            print(f"{ERR_MSG} You can still get your data from"
                  "the local cache.")
        except AttributeError:
            print("Update method is not available for this object.")
