import os
import json
from collections import Counter
from grab import Grab


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
        self.__data = Data(self.__login)

        self.playlist = Playlist(*self.__data.get_parsed())

    def update(self):
        """Update locally cached JSON file."""
        self.__data.update()

class Playlist:
    def __init__(self, *args):
        self.artists, self.genres, self.total_duration, self.total_duration_ms, self.tracks_count = args

class Data:
    def __init__(self, login):
        self.__login = login
        self.__json = self.__get_cache()

        if not self.__json:
            http = Connection()
            http.connect(self.__login)
            self.__json = http.get_json()

        self.__playlist = self.__get_playlist()

        self.__cache()

    def get_parsed(self):
        """Parse JSON data."""
        artists = Counter()
        genres = Counter()
        total_ms = 0

        for track in self.__playlist["tracks"]:
            for artist in track["artists"]:
                artists.update({f"{artist['name']}": 1})

            for album in track["albums"]:
                genre = album.get("genre")
                if genre:
                    genres.update({f"{genre}": 1})

            total_ms += track["durationMs"]

        return artists, genres, self.__format_ms(total_ms), total_ms, self.__get_tracks_count()

    def update(self):
        """Update locally cached JSON file."""
        http = Connection()
        http.connect(self.__login)
        self.__json = http.get_json()
        self.__cache(update=True)

    def __get_cache(self):
        """Get locally cached JSON file, if it exists."""
        try:
            with open(f"cache/{self.__login}.json", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def __get_playlist(self):
        try:
            playlist = self.__json["playlist"]
        except KeyError:
            print(f"The user '{self.__login}' does not exist!")
            raise

        try:
            playlist["tracks"]
        except KeyError:
            print(f"The account of the user '{self.__login}' is private!")
            raise

        return playlist

    def __cache(self, update=False):
        """Cache JSON file to the disk."""
        try:
            os.mkdir("cache")
        except FileExistsError:
            pass

        if os.path.exists(f"cache/{self.__login}.json") and not update:
            return

        with open(f"cache/{self.__login}.json", "w", encoding="utf-8") as file:
            json.dump(self.__json, file, ensure_ascii=False)

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

    def __get_tracks_count(self):
        return self.__playlist["trackCount"]

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
