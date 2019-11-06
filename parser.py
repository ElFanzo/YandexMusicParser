import os
import json
from collections import Counter
from grab import Grab


class MusicParser:
    def __init__(self, login: str):
        self.login = login
        self.artists = None
        self.genres = None
        self.json = self.__get_local_copy()

        self.__grab = None

        if not self.json:
            self.__connect()
            self.__get_json()

        self.__tracks = self.__get_tracks()

        self.__save_json()

    def __get_local_copy(self):
        try:
            with open(f"cache/{self.login}.json", encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def __connect(self):
        self.__grab = Grab(transport="urllib3")
        self.__grab.go(f"https://music.yandex.ru/handlers/playlist.jsx?owner={self.login}&kinds=3")

    def __get_json(self):
        self.json = self.__grab.doc.json

    def __save_json(self):
        try:
            os.mkdir("cache")
        except FileExistsError:
            pass

        if f"{self.login}.json" in os.listdir("cache"):
            return

        with open(f"cache/{self.login}.json", "w", encoding="utf-8") as file:
            json.dump(self.json, file, ensure_ascii=False)

    def __get_tracks(self):
        try:
            playlist = self.json["playlist"]
        except KeyError:
            print(f"The user {self.login} does not exist!")
            raise
        try:
            return playlist["tracks"]
        except KeyError:
            print(f"The account of the user {self.login} is private!")
            raise

    def get_genres(self):
        genres = Counter()

        for track in self.__tracks:
            for album in track["albums"]:
                genre = album.get("genre")
                if genre:
                    genres.update({f"{genre}": 1})

        return genres

    def get_artists(self):
        artists = Counter()

        for track in self.__tracks:
            for artist in track["artists"]:
                artists.update({f"{artist['name']}": 1})

        return artists
