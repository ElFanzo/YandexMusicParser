import json
import os
from collections import Counter

from database import DataCtx
from log import flash
from network import Connection


class Data:
    """The class for JSON data proccessing.

    All data is saved to the 'cache' folder in the JSON format.
    Each time all the necessary information is taken from the JSON cache.

    Args:
        login: a user's login

    Attributes:
        json: data in the JSON format
    """

    def __init__(self, login: str):
        self.__login = login
        self.__ctx = DataCtx()
        self.__uid = None

        if self.__is_user_exists():
            self.update()
        else:
            self.download()

        #self.json = self.__get_cache()

        #if not self.json:
        #    self.__check()
        #    self.update()

    def update(self):
        """Update locally cached JSON file."""
        pass

    def download(self):
        self.__check()

        common = self.__common_info()

        self.__add_user(common)

        self.__add_playlists(common)

        self.__add_playlist_tracks(common)

    def __is_user_exists(self):
        return self.__ctx.select(
            "select count(*) from user where login = ?", (self.__login,)
        )[0] == 1

    def __add_user(self, common):
        self.__uid = common["owner"]["uid"]
        name = common["owner"]["name"]
        playlists_count = len(common["playlistIds"])

        query = "insert into user values (?, ?, ?, ?)"
        self.__ctx.execute(
            query, (self.__uid, self.__login, name, playlists_count)
        )

    def __add_playlists(self, common):
        for playlist in common["playlists"]:
            _id = playlist["kind"]
            title = playlist["title"]   #  TODO: clearify title!
            tracks_count = playlist["trackCount"]
            modified = playlist.get("modified")

            query = "insert into playlist values (?, ?, ?, ?)"
            self.__ctx.execute(
                query, (self.__uid, _id, title, tracks_count, 0, modified)
            )

    def __add_track(self, track):
        # add to table

        self.__add_artists()

        # set relation

    def __add_artists(self, artists):
        # add to table

    def __common_info(self):
        http = Connection("playlists", self.__login)
        self.__common = http.get_json()

    def __get_playlist(self, _id):
        http = Connection("playlist", self.__login, _id)
        return http.get_json()["playlist"]

    def __add_playlist_tracks(self, common):
        for _id in common["playlistIds"]:
            js = self.__get_playlist(_id)

            for track in js["tracks"]:
                self.__add_track(track)
                # set relation

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
