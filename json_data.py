from query import Query
from log import flash
from network import Connection


class Data:
    """The class for JSON data proccessing.

    All data is saved to the 'cache' folder in the JSON format.
    Each time all the necessary information is taken from the JSON cache.

    Args:
        login: a user's login
    """

    def __init__(self, login: str):
        self.__query = Query()
        self.__query.init_tables()

        self.__login = login
        self.__uid = self.__query.get_uid(self.__login)

        if not self.__uid:
            self.__check()
            self.__download()

    def update(self):
        """Update database."""
        common = self.__common_info()
        local_ids = self.__query.get_playlists_ids(self.__uid)
        remote_ids = common["playlistIds"]
        diff = Data.get_differences(local_ids, remote_ids)

        self.add_delete_playlists(common, diff, local_ids, remote_ids)

        existed_ids = set(local_ids) - (diff["delete"] if diff else set())
        self.update_existed(
            [i for i in common["playlists"] if i["kind"] in existed_ids]
        )

        self.__query.delete_unused()

    def add_delete_playlists(self, common, diff, local_ids, remote_ids):
        """Add new, delete existed."""
        if diff:
            if diff["add"]:
                self.add_new_playlists(common, diff["add"])
            if diff["delete"]:
                self.__query.delete_playlists(self.__uid, diff["delete"])

            self.__query.update_playlists_count(self.__uid, len(remote_ids))

    def add_new_playlists(self, common, ids):
        self.__add_playlists(common, ids)
        self.__add_playlists_tracks(ids)

    def update_existed(self, existed):
        for playlist in existed:
            _id = playlist["kind"]
            new_title = playlist["title"]
            new_modified = playlist.get("modified")

            if self.__query.get_playlist_title(self.__uid, _id) != new_title:
                self.__query.update_playlist_title(self.__uid, _id, new_title)

            if not new_modified:
                self.update_playlist(_id)
            elif self.__query.get_modified(self.__uid, _id) != new_modified:
                self.update_playlist(_id)
                self.__query.update_modified(self.__uid, _id, new_modified)

    def update_playlist(self, _id):
        playlist = self.__get_playlist(_id)
        local_ids = self.__query.get_playlist_tracks_ids(self.__uid, _id)
        remote_ids = [int(i.split(":")[0]) for i in playlist["trackIds"]]

        diff = Data.get_differences(local_ids, remote_ids)
        if diff:
            if diff["add"]:
                self.__add_tracks(playlist["tracks"], _id, diff["add"])
            if diff["delete"]:
                self.__query.delete_tracks(self.__uid, _id, diff["delete"])

            self.__query.update_tracks_count(self.__uid, _id)
            self.__query.update_playlist_duration(self.__uid, _id)

    @staticmethod
    def get_differences(local_ids, remote_ids):
        local_set = set(local_ids)
        remote_set = set(remote_ids)
        diff = {
            "add": remote_set - local_set,
            "delete": local_set - remote_set
        }

        return diff if diff["add"] or diff["delete"] else None

    def __check(self):
        """Check if profile is private or does not exist."""
        js = Connection().get_json("info", self.__login)

        try:
            access = js["visibility"]
        except KeyError:
            flash(msg="ERR_USER", login=self.__login)
            raise

        if access == "private":
            flash(msg="ERR_ACCESS", login=self.__login)
            raise KeyError

    def __download(self):
        common = self.__common_info()

        self.__add_user(common)

        self.__add_playlists(common, common["playlistIds"])

        self.__add_playlists_tracks(common["playlistIds"])

    def __common_info(self):
        return Connection().get_json("playlists", self.__login)

    def __add_user(self, common):
        self.__uid = common["owner"]["uid"]
        name = common["owner"]["name"]
        playlists_count = len(common["playlistIds"])

        self.__query.insert_user(self.__uid, self.__login, name, playlists_count)

    def __add_playlists(self, common, ids_to_add):
        params = [
            (
                self.__uid,
                playlist["kind"],
                playlist["title"],
                playlist["trackCount"],
                0,
                playlist.get("modified")
            ) for playlist in common["playlists"] if playlist["kind"] in ids_to_add
        ]

        self.__query.insert_playlists(params)

    def __add_playlists_tracks(self, ids):
        for _id in ids:
            playlist = self.__get_playlist(_id)
            self.__add_tracks(
                playlist["tracks"],
                _id,
                set([int(str(i).split(":")[0]) for i in playlist["trackIds"]])
            )

            self.__query.update_playlist_duration(self.__uid, _id)

    def __add_tracks(self, tracks, playlist_id, ids_to_add):
        tracks_ids = self.__query.get_tracks_ids()
        params = []

        for track in tracks:
            track_id = int(track["id"])

            if (track_id not in tracks_ids) and (track_id in ids_to_add):
                params.append(
                    (
                        track_id,
                        track["title"],
                        track["albums"][0].get("year"),
                        track["albums"][0].get("genre"),
                        track["durationMs"]
                    )
                )
                tracks_ids.append(track_id)

        self.__query.insert_tracks(params)

        params = [(self.__uid, playlist_id, _id) for _id in ids_to_add]
        self.__query.insert_playlist_tracks(params)

        self.__add_artists(tracks, ids_to_add)

    def __add_artists(self, tracks, ids_to_add):
        artists_ids = self.__query.get_artists_ids()
        artists_params = []
        artist_track_params = []

        for track in tracks:
            if int(track["id"]) in ids_to_add:
                for artist in track["artists"]:
                    artist_id = int(artist["id"])

                    if artist_id not in artists_ids:
                        artists_params.append((artist_id, artist["name"]))
                        artists_ids.append(artist_id)

                    artist_track_params.append((artist_id, track["id"]))

        self.__query.insert_artists(artists_params)
        self.__query.insert_artist_track(artist_track_params)

    def __get_playlist(self, _id):
        return Connection().get_json("playlist", self.__login, _id)["playlist"]
