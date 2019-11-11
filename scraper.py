from grab.error import GrabConnectionError

from json_data import Data
from models import Playlist
from log import flash


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
            flash(msg="ERR_MSG")
        except KeyError:
            pass
        else:
            self.playlist = Playlist(self.__data.json)

    def update(self):
        """Update the locally cached JSON file."""
        flash(msg="UPD")
        try:
            self.__data.update()
        except GrabConnectionError:
            flash(msg="ERR_NET_BUT_CACHE")
        except AttributeError:
            flash(msg="ERR_UPD")
