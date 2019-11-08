from grab import Grab


class Connection:
    """Connect to the Yandex Music site and download response."""
    def __init__(self):
        self.__grab = Grab(transport="urllib3")

    def connect(self, login):
        """Connect to the Yandex Music site."""
        url = ("https://music.yandex.ru/handlers/playlist.jsx"
               f"?owner={login}&kinds=3")
        self.__grab.go(url)

    def get_json(self):
        """Get response in the JSON format."""
        return self.__grab.doc.json