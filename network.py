from grab import Grab


class Connection:
    def __init__(self):
        self.__grab = Grab(transport="urllib3")

    def connect(self, login):
        """Connect to the Yandex Music site."""
        url = ("https://music.yandex.ru/handlers/playlist.jsx"
               f"?owner={login}&kinds=3")
        self.__grab.go(url)

    def get_json(self):
        return self.__grab.doc.json
