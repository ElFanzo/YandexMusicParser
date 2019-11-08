import os
import json
from collections import Counter
from grab import Grab
from grab.error import GrabConnectionError


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

class Playlist:
    def __init__(self, _json):
        self.artists = _json["artists"]
        self.genres = _json["genres"]
        self.total_duration = _json["total_duration"]
        self.total_duration_ms = _json["total_duration_ms"]
        self.tracks_count = _json["tracks_count"]

class Data:
    def __init__(self, login):
        self.__login = login
        self.json = self.__get_cache()

        if not self.json:
            self.update()

    def update(self):
        """Update locally cached JSON file."""
        self.json = self.__get_parsed()
        self.__cache()

    def __get_cache(self):
        """Get locally cached JSON file, if it exists."""
        try:
            with open(f"cache/{self.__login}.json", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def __get_parsed(self):
        """Parse JSON data."""
        http = Connection()
        http.connect(self.__login)
        playlist = self.__get_playlist(http.get_json())

        artists = Counter()
        genres = Counter()
        total_ms = 0

        for track in playlist["tracks"]:
            for artist in track["artists"]:
                artists.update({f"{artist['name']}": 1})

            for album in track["albums"]:
                genre = album.get("genre")
                if genre:
                    genres.update({f"{genre}": 1})

            total_ms += track["durationMs"]

        result = json.loads("{}")
        result["artists"] = dict(artists.most_common())
        result["genres"] = dict(genres.most_common())
        result["total_duration"] = Data.__format_ms(total_ms)
        result["total_duration_ms"] = total_ms
        result["tracks_count"] = playlist["trackCount"]

        return result

    def __get_playlist(self, json_body):
        try:
            playlist = json_body["playlist"]
        except KeyError:
            print(f"The user '{self.__login}' does not exist!")
            raise

        try:
            playlist["tracks"]
        except KeyError:
            print(f"The account of the user '{self.__login}' is private!")
            raise

        return playlist

    def __cache(self):
        """Cache JSON file to the disk."""
        try:
            os.mkdir("cache")
        except FileExistsError:
            pass

        with open(f"cache/{self.__login}.json", "w", encoding="utf-8") as file:
            json.dump(self.json, file, ensure_ascii=False)

    @staticmethod
    def __format_ms(total_ms: int) -> str:
        """Format milliseconds to the string.

        :param total_ms: a number of milliseconds
        :return: "%H h. %M min. %S sec." format string
        """
        seconds = total_ms // 1000
        minutes = seconds // 60
        hours = minutes // 60

        return f"{hours} h. {minutes % 60} min. {seconds % 60} sec."

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
