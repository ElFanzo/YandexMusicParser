import re

from urllib3.exceptions import MaxRetryError, TimeoutError

from .exceptions import LoginError, NetworkError
from .log import flash
from .models import Artist, Playlist, Track, User
from .query import Query, UserQuery
from .service import Service


class Client:
    """A client's class.

    Only a user with the public account can be a client.

    Args:
        login: a Yandex Music account's login

    Attributes:
        user: User object
    """

    def __init__(self, login: str):
        self.user = None

        self._login = self._clean_login(login)

        try:
            self._service = Service(self._login)
        except (MaxRetryError, TimeoutError):
            raise NetworkError from None
        else:
            self._set_data()
            flash(msg="USER_SUCCESS")

    def update(self):
        """Update client's data."""
        flash(msg="UPD")

        try:
            self._service.update()
        except (MaxRetryError, TimeoutError):
            raise NetworkError from None

        self._set_data()
        flash(msg="DONE")

    @staticmethod
    def _clean_login(login):
        if not login or not isinstance(login, str):
            raise LoginError()

        return re.sub(r"@ya\w{,4}\.\w{,3}", "", login.strip().lower())

    def _set_data(self):
        """Create a user and other entities from the database data."""
        query = Query(self._login)
        user_query = UserQuery(self._login)

        db_playlists = query.get_user_playlists()

        self._set_user(user_query, len(db_playlists))

        for playlist in db_playlists:
            self._set_playlists(user_query, playlist)

        for playlist in self.user.playlists:
            Client._set_tracks_artists(query, playlist)

    def _set_user(self, query, playlists_count):
        self.user = User(query, self._login, playlists_count, [])

    def _set_playlists(self, query, playlist):
        self.user.playlists.append(Playlist(query, *playlist, tracks=[]))

    @staticmethod
    def _set_tracks_artists(query, playlist):
        all_tracks = {
            i[0]: Track(*i, artists=[], artists_count=0)
            for i in query.get_playlist_tracks(playlist.id_)
        }
        all_artists = {
            i[0]: Artist(
                *i, tracks=[], tracks_count=0,
                genres=query.get_artist_genres(i[0])
            )
            for i in query.get_playlist_artists(playlist.id_)
        }

        Client._bind_artists_to_tracks(query, all_tracks, all_artists)
        Client._bind_tracks_to_artists(
            query, all_tracks, all_artists, playlist.id_
        )

        playlist.tracks = [i for i in all_tracks.values()]
        playlist.tracks_count = len(playlist.tracks)

    @staticmethod
    def _bind_artists_to_tracks(query, tracks, artists):
        for track_id, track in tracks.items():
            artists_ids = query.get_track_artists_ids(track_id)
            for artist_id in artists_ids:
                track.artists.append(artists[artist_id])
            track.artists_count = len(artists_ids)

    @staticmethod
    def _bind_tracks_to_artists(query, tracks, artists, playlist_id):
        for artist_id, artist in artists.items():
            tracks_ids = query.get_artist_tracks_ids(playlist_id, artist_id)
            for track_id in tracks_ids:
                artist.tracks.append(tracks[track_id])
            artist.tracks_count = len(tracks_ids)
