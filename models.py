class Playlist:
    """The scraped data storing.

    Available data:
        artists: dict
        genres: dict
        total_duration: str
        total_duration_ms: int
        tracks_count: int
    """
    def __init__(self, _json):
        self.artists = _json["artists"]
        self.genres = _json["genres"]
        self.total_duration = _json["total_duration"]
        self.total_duration_ms = _json["total_duration_ms"]
        self.tracks_count = _json["tracks_count"]