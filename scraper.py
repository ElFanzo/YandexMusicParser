from grab.error import GrabConnectionError

from json_data import Data
from models import Playlist

ERR_MSG = "Internet is not available. Please, check your connection and try again."

class MusicParser:
    """The class for collecting data from the Yandex Music site.

    It works only with public accounts.

    Available data:
        artists: Counter object
        genres: Counter object
        total_duration: str
        total_duration_ms: int
        tracks_count: int

    All scraped data is saved to the 'cache' folder in the JSON format.
    Each time all the necessary information is taken from the JSON cache.
    The cache can be updated by the 'update' method, if necessary.

    :param login: Yandex Music account's login
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
        """Update locally cached JSON file."""
        try:
            self.__data.update()
        except GrabConnectionError:
            print(f"{ERR_MSG} You can still get your data from the local cache.")
        except AttributeError:
            print("Update method is not available for this object.")
