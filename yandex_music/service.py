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
        self._login = login
        flash(msg="DB_SEARCH")
        self._query = Query(login)

        if not self._query.user_name:
            flash(msg="DB_FAIL")
            self._check()
            flash(msg="DB_DOWNLOAD")
            self._download()

    def update(self):
        """Update database."""
        common = self._common_info()
        local_ids = self._query.get_playlists_ids()
        remote_ids = common["playlistIds"]
        diff = Service._get_differences(local_ids, remote_ids)

        self._add_delete_playlists(common, diff, remote_ids)

        existed_ids = set(local_ids) - (diff["delete"] if diff else set())
        self._update_existed(
            [i for i in common["playlists"] if i["kind"] in existed_ids]
        )

        self._query.delete_unused()

    def _add_artists(self, tracks, ids_to_add):
        artists_ids = self._query.get_artists_ids()
        artist_track_ids = self._query.get_artist_track_ids()
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

        self._query.insert_artists(artists_params)
        self._query.insert_artist_track(artist_track_params)

    def _add_delete_playlists(self, common, diff, remote_ids):
        """Add new, delete existed."""
        if diff:
            if diff["add"]:
                self._add_new_playlists(common, diff["add"])
            if diff["delete"]:
                self._query.delete_playlists(diff["delete"])

            self._query.update_playlists_count(len(remote_ids))

    def _add_new_playlists(self, common, ids):
        self._add_playlists(common, ids)
        self._add_playlists_tracks(ids)

    def _add_playlists(self, common, ids_to_add):
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

        self._query.insert_playlists(params)

    def _add_playlists_tracks(self, ids):
        for _id in ids:
            playlist = self._get_playlist(_id)
            self._add_tracks(
                playlist["tracks"],
                _id,
                set([int(str(i).split(":")[0]) for i in playlist["trackIds"]])
            )

            self._query.update_playlist_duration(_id)

    def _add_tracks(self, tracks, playlist_id, ids_to_add):
        tracks_ids = self._query.get_tracks_ids()
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

        self._query.insert_tracks(params)

        params = [(playlist_id, _id) for _id in ids_to_add]
        self._query.insert_playlist_tracks(params)

        self._add_artists(tracks, ids_to_add)

    def _add_user(self, common):
        uid = common["owner"]["uid"]
        name = common["owner"]["name"]
        playlists_count = len(common["playlistIds"])

        self._query.insert_user(uid, self._login, name, playlists_count)

    def _check(self):
        """Check a user's profile for the possibility to get his data."""
        js = Connection().get_json("info", self._login)

        access = js.get("visibility")
        if not access:
            raise UserDoesNotExistError(self._login)

        if access != "public":
            raise AccessError(self._login)

        if not js["hasTracks"]:
            raise NoTracksError(self._login)

    def _common_info(self):
        return Connection().get_json("playlists", self._login)

    def _download(self):
        common = self._common_info()

        self._add_user(common)

        self._add_new_playlists(common, common["playlistIds"])

    @staticmethod
    def _get_differences(local_ids, remote_ids):
        local_set = set(local_ids)
        remote_set = set(remote_ids)
        diff = {
            "add": remote_set - local_set,
            "delete": local_set - remote_set
        }

        return diff if diff["add"] or diff["delete"] else None

    def _get_playlist(self, _id):
        return Connection().get_json(
            "playlist", self._login, _id
        )["playlist"]

    def _update_existed(self, existed):
        for playlist in existed:
            _id = playlist["kind"]
            new_title = playlist["title"]
            new_modified = playlist.get("modified")

            if self._query.get_playlist_title(_id) != new_title:
                self._query.update_playlist_title(_id, new_title)

            if not new_modified:
                self._update_playlist(_id)
            elif self._query.get_modified(_id) != new_modified:
                self._update_playlist(_id)
                self._query.update_modified(_id, new_modified)

    def _update_playlist(self, _id):
        playlist = self._get_playlist(_id)
        local_ids = self._query.get_playlist_tracks_ids(_id)
        remote_ids = [int(str(i).split(":")[0]) for i in playlist["trackIds"]]

        diff = Service._get_differences(local_ids, remote_ids)
        if diff:
            if diff["add"]:
                self._add_tracks(playlist["tracks"], _id, diff["add"])
            if diff["delete"]:
                self._query.delete_tracks(_id, diff["delete"])

            self._query.update_tracks_count(_id)
            self._query.update_playlist_duration(_id)
