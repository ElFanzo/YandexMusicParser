from grab import Grab

BASE_URL = "https://music.yandex.ru/handlers"
URLS = {
    "info": f"{BASE_URL}" "/library.jsx?owner={}",
    "playlists": f"{BASE_URL}" "/library.jsx?owner={}&filter=playlists",
    "playlist": f"{BASE_URL}" "/playlist.jsx?owner={}&kinds={}",
}


class Connection:
    """Connect to the Yandex Music site and download response."""

    def __init__(self):
        self.__grab = Grab(transport="urllib3")

    def get_json(self, subject, *args):
        """Get response in the JSON format."""
        self.__connect(subject, *args)

        return self.__grab.doc.json

    def __connect(self, subject, *args):
        """Connect to the Yandex Music site."""
        url = URLS[subject].format(*args)
        self.__grab.go(url)
