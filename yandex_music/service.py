from .exceptions import AccessError, NoTracksError, UserDoesNotExistError
from .log import flash
from .network import Connection
from .query import Query


class Service:
    """A user's data proccessing.

    Args:
        login: the user's login
    """

    def __init__(self, login: str):
        self.__login = login
        flash(msg="DB_SEARCH")
        self.__query = Query(login)

        if not self.__query.user_name:
            flash(msg="DB_FAIL")
            self.__check()
            flash(msg="DB_DOWNLOAD")
            self.__download()

    def update(self):
        """Update database."""
        common = self.__common_info()
        local_ids = self.__query.get_playlists_ids()
        remote_ids = common["playlistIds"]
        diff = Service.__get_differences(local_ids, remote_ids)

        self.__add_delete_playlists(common, diff, remote_ids)

        existed_ids = set(local_ids) - (diff["delete"] if diff else set())
        self.__update_existed(
            [i for i in common["playlists"] if i["kind"] in existed_ids]
        )

        self.__query.delete_unused()

    def __add_artists(self, tracks, ids_to_add):
        artists_ids = self.__query.get_artists_ids()
        artist_track_ids = self.__query.get_artist_track_ids()
        artists_params = []
        artist_track_params = []

        for track in tracks:
            track_id = int(track["id"])
            if track_id in ids_to_add:
                for artist in track["artists"]:
                    artist_track = (int(artist["id"]), track_id)

                    if artist_track[0] not in artists_ids:
                        artists_params.append(
                            (artist_track[0], artist["name"])
                        )
                        artists_ids.append(artist_track[0])

                    if artist_track not in artist_track_ids \
                            and artist_track not in artist_track_params:
                        artist_track_params.append(artist_track)

        self.__query.insert_artists(artists_params)
        self.__query.insert_artist_track(artist_track_params)

    def __add_delete_playlists(self, common, diff, remote_ids):
        """Add new, delete existed."""
        if diff:
            if diff["add"]:
                self.__add_new_playlists(common, diff["add"])
            if diff["delete"]:
                self.__query.delete_playlists(diff["delete"])

            self.__query.update_playlists_count(len(remote_ids))

    def __add_new_playlists(self, common, ids):
        self.__add_playlists(common, ids)
        self.__add_playlists_tracks(ids)

    def __add_playlists(self, common, ids_to_add):
        params = [
            (
                playlist["kind"],
                playlist["title"],
                playlist["trackCount"],
                0,
                playlist.get("modified")
            )
            for playlist in common["playlists"]
            if playlist["kind"] in ids_to_add
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

            self.__query.update_playlist_duration(_id)

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

        params = [(playlist_id, _id) for _id in ids_to_add]
        self.__query.insert_playlist_tracks(params)

        self.__add_artists(tracks, ids_to_add)

    def __add_user(self, common):
        uid = common["owner"]["uid"]
        name = common["owner"]["name"]
        playlists_count = len(common["playlistIds"])

        self.__query.insert_user(uid, self.__login, name, playlists_count)

    def __check(self):
        """Check a user's profile for the possibility to get his data."""
        js = Connection().get_json("info", self.__login)

        access = js.get("visibility")
        if not access:
            raise UserDoesNotExistError(self.__login)

        if access != "public":
            raise AccessError(self.__login)

        if not js["hasTracks"]:
            raise NoTracksError(self.__login)

    def __common_info(self):
        return Connection().get_json("playlists", self.__login)

    def __download(self):
        common = self.__common_info()

        self.__add_user(common)

        self.__add_new_playlists(common, common["playlistIds"])

    @staticmethod
    def __get_differences(local_ids, remote_ids):
        local_set = set(local_ids)
        remote_set = set(remote_ids)
        diff = {
            "add": remote_set - local_set,
            "delete": local_set - remote_set
        }

        return diff if diff["add"] or diff["delete"] else None

    def __get_playlist(self, _id):
        return Connection().get_json(
            "playlist", self.__login, _id
        )["playlist"]

    def __update_existed(self, existed):
        for playlist in existed:
            _id = playlist["kind"]
            new_title = playlist["title"]
            new_modified = playlist.get("modified")

            if self.__query.get_playlist_title(_id) != new_title:
                self.__query.update_playlist_title(_id, new_title)

            if not new_modified:
                self.__update_playlist(_id)
            elif self.__query.get_modified(_id) != new_modified:
                self.__update_playlist(_id)
                self.__query.update_modified(_id, new_modified)

    def __update_playlist(self, _id):
        playlist = self.__get_playlist(_id)
        local_ids = self.__query.get_playlist_tracks_ids(_id)
        remote_ids = [int(str(i).split(":")[0]) for i in playlist["trackIds"]]

        diff = Service.__get_differences(local_ids, remote_ids)
        if diff:
            if diff["add"]:
                self.__add_tracks(playlist["tracks"], _id, diff["add"])
            if diff["delete"]:
                self.__query.delete_tracks(_id, diff["delete"])

            self.__query.update_tracks_count(_id)
            self.__query.update_playlist_duration(_id)
