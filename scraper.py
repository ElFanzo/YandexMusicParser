from grab.error import GrabConnectionError

from json_data import Data
from log import flash
from models import Artist, Playlist, User, Track


class Client:
    """A client's class.

    Only a user with the public account can be a client.

    Args:
        login: a Yandex Music account's login

    Attributes:
        user: User object
    """

    def __init__(self, login: str):
        self.user = None

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
        """Update client's data."""
        flash(msg="UPD")
        try:
            self.__data.update()
            self.__set_data()
        except GrabConnectionError:
            flash(msg="ERR_NET_BUT_CACHE")
        except AttributeError:
            flash(msg="ERR_UPD")

    def __set_data(self):
        # self.user = User(self.__login, ...)
        # playlists, tracks, artists...
        pass
