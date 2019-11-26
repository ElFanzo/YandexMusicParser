from datetime import datetime, timezone

from log import flash
from network import Connection


class Artist:
    """An artist's data storing class.

    Args:
        id_: the artist's real id
        name: the artist's name
        tracks: a list of the artist's tracks
        tracks_count: the artist's tracks count
        genres: the artist's genres

    Attributes:
        id_:
        name:
        tracks:
        tracks_count:
        genres:
    """

    def __init__(self, id_: int, name: str, tracks: list,
                 tracks_count: int, genres: list):
        self.id_ = id_
        self.name = name
        self.tracks = tracks
        self.tracks_count = tracks_count
        self.genres = genres

        self.__likes = None

    def get_likes(self):
        """Get the amount of the artist's likes."""
        if self.__likes:
            return self.__likes

        js = Connection().get_json("artist", self.id_)
        try:
            return js["artist"]["likesCount"]
        except KeyError:
            return None

    def __str__(self):
        return f"Artist({self.name}, {len(self.tracks)} track(s))"


class Playlist:
    """A playlist's data storing class.

    Args:
        query: UserQuery object for queries execution
        id_: the playlist's kind value
        title: the playlist's title
        tracks: a list of the playlist's tracks
        tracks_count: the playlist's tracks count
        duration: total duration of the playlist
        modified: last modified datetime

    Attributes:
        id_:
        title:
        tracks:
        tracks_count:
        duration: total duration in the "%H h. %M min. %S sec." format
        duration_ms: total durartion in milliseconds
        modified:
    """

    def __init__(self, query, id_: int, title: str, tracks_count: int,
                 duration: int, modified: str, tracks: list):
        self.id_ = id_
        self.title = title
        self.tracks = tracks
        self.tracks_count = tracks_count
        self.duration_ms = duration
        self.duration = Playlist.__format_ms(self.duration_ms)
        self.modified = Playlist.__utc_to_local(modified) \
            if modified else None

        self.__query = query

    def get_artists_counter(self):
        """Get a dict with {Artist name: count} items."""
        return self.__query.get_artists_counter(self.id_)

    def get_genres_counter(self):
        """Get a dict with {Genre: count} items."""
        return self.__query.get_genres_counter(self.id_)

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

    @staticmethod
    def __utc_to_local(date_utc: str) -> datetime:
        date_utc = datetime.fromisoformat(date_utc)
        return date_utc.replace(tzinfo=timezone.utc).astimezone()

    def __str__(self):
        return f"Playlist({self.title}, {len(self.tracks)} track(s))"


class Track:
    """A track's data storing class.

    Args:
        id_: the track's real id
        title: the track's title
        artists: a list of track's artists
        artists_count: the track's artists count
        year: the track's release year
        genre: the track's genre
        duration: duration of the track

    Attributes:
        id_:
        title:
        artists:
        artists_count:
        year:
        genre:
        duration: duration in the "%M min. %S sec." format
        duration_ms: duration in milliseconds
    """

    def __init__(self, id_: int, title: str, year: int, genre: str,
                 duration: int, artists: list, artists_count: int):
        self.id_ = id_
        self.title = title
        self.artists = artists
        self.artists_count = artists_count
        self.year = year
        self.genre = genre
        self.duration_ms = duration
        self.duration = Track.__format_ms(self.duration_ms)

    @staticmethod
    def __format_ms(total_ms: int) -> str:
        """Format milliseconds to the string.

        :param total_ms: a number of milliseconds
        :return: "%M min. %S sec." format string
        """
        seconds = total_ms // 1000
        minutes = seconds // 60

        return f"{minutes} min. {seconds % 60} sec."

    def __str__(self):
        return f"{' ft. '.join([i.name for i in self.artists])}"\
               f" - {self.title}"


class User:
    """A user's data storing class.

    Args:
        query: the UserQuery object for queries execution
        login: the user's login
        playlists: a list of the user's playlists
        playlists_count: the user's playlists count

    Attributes:
        login:
        name: the user's name
        playlists:
        playlists_count:
    """

    def __init__(self, query, login: str, playlists_count: int,
                 playlists: list):
        self.login = login
        self.name = query.user_name
        self.playlists = playlists
        self.playlists_count = playlists_count

        self.__query = query

    def delete(self):
        """Delete all the user's data from the database."""
        if self.__query.user_name:
            self.__query.delete_user_data()
            flash(msg="DEL_SUCCESS", login=self.login)
        else:
            flash(msg="DEL_ALREADY", login=self.login)

    def __str__(self):
        return (
            f"User {self.login}({self.name}, "
            f"{len(self.playlists)} playlist(s))"
        )
