from json import loads

from urllib3 import PoolManager

BASE_URL = "https://music.yandex.ru/handlers"
URLS = {
    "info": f"{BASE_URL}" "/library.jsx?owner={}",
    "playlists": f"{BASE_URL}" "/library.jsx?owner={}&filter=playlists",
    "playlist": f"{BASE_URL}" "/playlist.jsx?owner={}&kinds={}",
    "artist": f"{BASE_URL}" "/artist.jsx?artist={}",
}


class Connection:
    """Connect to the Yandex Music site and download response."""

    def __init__(self):
        self.__http = PoolManager()

    def get_json(self, subject, *args):
        """Get response in the JSON format."""
        return loads(self.__response(subject, *args))

    def __response(self, subject, *args):
        """Get response from the Yandex Music site."""
        url = URLS[subject].format(*args)
        return self.__http.request("GET", url).data
