import os
import json
from collections import Counter

from network import Connection
from log import flash


class Data:
    """The class for JSON data proccessing.

    All data is saved to the 'cache' folder in the JSON format.
    Each time all the necessary information is taken from the JSON cache.

    :param json: data in the JSON format
    """

    def __init__(self, login: str):
        self.__login = login
        self.json = self.__get_cache()

        if not self.json:
            self.__check()
            self.update()

    def update(self):
        """Update locally cached JSON file."""
        self.json = self.__get_json_list()
        self.__cache()

    def __get_cache(self):
        """Get locally cached JSON file, if it exists."""
        flash(msg="CACHE_LOOK")
        try:
            with open(f"cache/{self.__login}.json", encoding="utf-8") as file:
                js = json.load(file)
            flash(msg="CACHE_SUCCESS")
            return js
        except (FileNotFoundError, json.JSONDecodeError):
            flash(msg="CACHE_FAIL")
            return None

    def __get_json_list(self):
        """Get a JSON list of playlists."""
        http = Connection("playlists", self.__login)
        _json = http.get_json()
        playlist_ids = _json["playlistIds"]
        jsons = json.loads('{"playlists":[]}')
        jsons["name"] = _json["owner"]["name"]

        for _id in playlist_ids:
            http = Connection("playlist", self.__login, _id)
            jsons["playlists"].append(self.__get_parsed(http.get_json()["playlist"]))

        return jsons

    def __get_parsed(self, playlist):
        """Get parsed JSON data for each playlist."""
        artists = Counter()
        genres = Counter()
        total_ms = 0

        for track in playlist["tracks"]:
            for artist in track["artists"]:
                artists.update({f"{artist['name']}": 1})

            genre = track["albums"][0].get("genre")
            if genre:
                genres.update({f"{genre}": 1})

            total_ms += track["durationMs"]

        result = json.loads("{}")
        result["title"] = playlist["title"]
        result["artists"] = dict(artists.most_common())
        result["genres"] = dict(genres.most_common())
        result["total_duration"] = Data.__format_ms(total_ms)
        result["total_duration_ms"] = total_ms
        result["tracks_count"] = playlist["trackCount"]

        return result

    def __check(self):
        """Check if profile is private or does not exist."""
        http = Connection("info", self.__login)
        js = http.get_json()

        try:
            access = js["visibility"]
        except KeyError:
            flash(msg="ERR_USER", login=self.__login)
            raise

        if access == "private":
            flash(msg="ERR_ACCESS", login=self.__login)
            raise KeyError

    def __cache(self):
        """Cache JSON file to the disk."""
        try:
            os.mkdir("cache")
        except FileExistsError:
            pass

        with open(f"cache/{self.__login}.json", "w", encoding="utf-8") as file:
            json.dump(self.json, file, ensure_ascii=False)

        flash(msg="DONE")

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
