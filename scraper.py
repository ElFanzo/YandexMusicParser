from grab.error import GrabConnectionError

from json_data import Data
from models import Playlist
from log import flash


class Listener:
    """The class for scraping data from the Yandex Music site.

    It works only with public accounts.

    :param login: the Yandex Music account's login
    :param playlists: resulting list of the Playlist objects
    """

    def __init__(self, login: str):
        self.name = None
        self.playlists = None

        self.__login = login
        try:
            self.__data = Data(self.__login)
        except GrabConnectionError:
            flash(msg="ERR_MSG")
        except KeyError:
            pass
        else:
            self.__set_data()

    def update(self):
        """Update the locally cached JSON file."""
        flash(msg="UPD")
        try:
            self.__data.update()
            self.__set_data()
        except GrabConnectionError:
            flash(msg="ERR_NET_BUT_CACHE")
        except AttributeError:
            flash(msg="ERR_UPD")

    def __set_data(self):
        self.name = self.__data.json["name"]
        self.playlists = [
                Playlist(js) for js in self.__data.json["playlists"]
        ]

    def __str__(self):
        return (f"User {self.__login}({self.name}, {len(self.playlists)} "
                "playlist(s))")
