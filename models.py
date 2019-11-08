class Playlist:
    def __init__(self, _json):
        self.artists = _json["artists"]
        self.genres = _json["genres"]
        self.total_duration = _json["total_duration"]
        self.total_duration_ms = _json["total_duration_ms"]
        self.tracks_count = _json["tracks_count"]
