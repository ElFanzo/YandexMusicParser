from datetime import datetime, timezone


class Artist:
    """An artist's data storing class.

    Args:
        name: the artist's name
        tracks: a list of the artst's tracks
        genres: the artist's genres

    Attributes:
        name:
        tracks:
        genres:
    """

    def __init__(self, name: str, tracks: list, genres: list):
        self.name = name
        self.tracks = tracks
        self.genres = genres

    def __str__(self):
        return f"Artist({self.name}, {len(self.tracks)} track(s))"


class Playlist:
    """A playlist's data storing class.

    Args:
        title: the playlist's title
        tracks: a list of the playlist's tracks
        duration: total duration of the playlist
        modified: last modified datetime

    Attributes:
        title:
        tracks:
        duration:
        duration_ms:
        modified:
    """

    def __init__(self, title: str, tracks: list, duration: int, modified: str):
        self.title = title
        self.tracks = tracks
        self.duration_ms = duration
        self.duration = Playlist.__format_ms(self.duration_ms)
        self.modified = Playlist.__utc_to_local(modified)

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
        return (date_utc.replace(tzinfo=timezone.utc).astimezone())

    def __str__(self):
        return f"Playlist({self.title}, {len(self.tracks)} track(s))"


class User:
    """A user's data storing class.

    Args:
        login: the user's login
        playlists: a list of the user's playlists

    Attributes:
        login:
        name: the user's name
        playlists:
    """

    def __init__(self, login: str, playlists: list):
        self.login = login
        self.name = self.get_name()
        self.playlists = playlists

    def get_name(self):
        pass

    def __str__(self):
        return (
            f"User {self.login}({self.name},"
            "{len(self.playlists)} playlist(s))"
        )


class Track:
    """Playlist's data storing class.

    Args:
        title: a playlist's title
        tracks: a list of playlist's tracks
        duration: total duration of the playlist
        modified: last modified datetime

    Attributes:
        title: str
        tracks: List<Track>
        duration: str
        duration_ms: int
        modified: datetime
    """

    def __init__(self, title: str, tracks: list, duration: int, modified: datetime):
        self.title = title
        self.artists = artists
        self.year = year
        self.genre = genre
        self.duration_ms = duration_ms
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
        return f"Track({self.title}, Artist(s): {self.artists})"
