from database import DataCtx


class BaseQuery:
    """Queries executing class."""

    def __init__(self, login: str):
        self._db = DataCtx()
        self.__init_tables()

        self.user_name, self._uid = self.__get_user_data(login)

    def delete_unused(self):
        self.__delete_unused_tracks()
        self.__delete_unused_artists()

    def __delete_unused_artists(self):
        self._db.execute(
            """delete from artist
               where id not in (
                 select artist_id from artist_track)"""
        )

    def __delete_unused_tracks(self):
        self._db.execute(
            """delete from track
               where id not in (
                 select track_id from playlist_track)"""
        )

    def __get_user_data(self, login: str):
        data = self._db.select(
            "select name, id from user where login = ?", (login,)
        )
        return data if data else (None, None)

    def __init_tables(self):
        self._db.execute_script(
            """PRAGMA foreign_keys = on;

            create table if not exists user (
                id integer primary key,
                login text unique not null,
                name text not null,
                playlists_count integer);

            create table if not exists playlist (
                user_id integer,
                id integer,
                title text not null,
                tracks_count integer,
                duration integer,
                modified text,
                primary key (user_id, id),
                foreign key (user_id) references user(id) on delete cascade);

            create table if not exists track (
                id integer primary key,
                title text not null,
                year integer,
                genre text,
                duration integer);

            create table if not exists artist (
                id integer primary key,
                name text not null);

            create table if not exists playlist_track (
                user_id integer,
                playlist_id integer,
                track_id integer,
                primary key (user_id, playlist_id, track_id)
                foreign key (user_id, playlist_id) references
                  playlist(user_id, id) on delete cascade,
                foreign key (track_id) references track(id)
                  on delete cascade);

            create table if not exists artist_track (
                artist_id integer,
                track_id integer,
                primary key (artist_id, track_id),
                foreign key (artist_id) references artist(id)
                  on delete cascade,
                foreign key (track_id) references track(id)
                  on delete cascade);"""
        )


class Query(BaseQuery):
    def delete_playlists(self, ids: list):
        signs = ", ".join(["?"] * len(ids))
        self._db.execute(
            f"delete from playlist where id in ({signs}) and user_id = ?",
            (*ids, self._uid)
        )

    def delete_tracks(self, playlist_id: int, ids: set):
        signs = ", ".join(["?"] * len(ids))
        self._db.execute(
            f"""delete from playlist_track
                where track_id in ({signs})
                  and user_id = ? and playlist_id = ?""",
            (ids, self._uid, playlist_id)
        )

    def get_artist_genres(self, _id):
        query = """select distinct track.genre
                   from track
                     inner join artist_track on track_id = id
                   where artist_id = ?"""
        return [i[0] for i in self._db.select_all(query, (_id,))]

    def get_artist_track_ids(self):
        return self._db.select_all("select * from artist_track")

    def get_artist_tracks_ids(self, playlist_id, artist_id):
        query = """select at.track_id
                   from artist_track at
                     inner join playlist_track pt on pt.track_id = at.track_id
                   where pt.user_id = ? and pt.playlist_id = ?
                     and at.artist_id = ?"""
        return [
            i[0] for i in self._db.select_all(
                query, (self._uid, playlist_id, artist_id,)
            )
        ]

    def get_artists_ids(self):
        return self.__get_ids("artist")

    def get_modified(self, _id: int):
        return self._db.select(
            """select modified from playlist
               where user_id = ? and id = ?""",
            (self._uid, _id)
        )[0]

    def get_playlist_artists(self, _id):
        query = """select distinct a.*
                   from artist a
                     inner join artist_track at on at.artist_id = a.id
                     inner join playlist_track pt on pt.track_id = at.track_id
                   where playlist_id = ? and user_id = ?"""
        return self._db.select_all(query, (_id, self._uid,))

    def get_playlist_title(self, _id: int):
        return self._db.select(
            """select title from playlist
               where user_id = ? and id = ?""",
            (self._uid, _id)
        )[0]

    def get_playlist_tracks(self, _id):
        query = """select track.*
                   from track
                     inner join playlist_track on track_id = id
                   where playlist_id = ? and user_id = ?"""
        return self._db.select_all(query, (_id, self._uid,))

    def get_playlist_tracks_ids(self, _id: int):
        return [
            i[0] for i in self._db.select_all(
                """select track_id from playlist_track
                   where user_id = ? and playlist_id = ?""",
                (self._uid, _id)
            )
        ]

    def get_playlists_ids(self):
        return [
            i[0] for i in self._db.select_all(
                "select id from playlist where user_id = ?", (self._uid,)
            )
        ]

    def get_track_artists_ids(self, _id):
        query = """select artist_id
                   from artist_track
                   where track_id = ?"""
        return [i[0] for i in self._db.select_all(query, (_id,))]

    def get_tracks_ids(self):
        return self.__get_ids("track")

    def get_user_playlists(self):
        query = """select id, title, tracks_count, duration, modified
                   from playlist where user_id = ?"""
        return self._db.select_all(query, (self._uid,))

    def insert_artist_track(self, params: list):
        self._db.execute_many(
            "insert into artist_track values (?, ?)", params
        )

    def insert_artists(self, params: list):
        self._db.execute_many("insert into artist values (?, ?)", params)

    def insert_playlist_tracks(self, params: list):
        params = self.__get_params_with_uid(params)
        self._db.execute_many(
            "insert into playlist_track values (?, ?, ?)", params
        )

    def insert_playlists(self, params: list):
        params = self.__get_params_with_uid(params)
        self._db.execute_many(
            "insert into playlist values (?, ?, ?, ?, ?, ?)", params
        )

    def insert_tracks(self, params: list):
        self._db.execute_many(
            "insert into track values (?, ?, ?, ?, ?)", params
        )

    def insert_user(self, *params):
        self._db.execute(
            "insert into user values (?, ?, ?, ?)", tuple(params)
        )
        self._uid = params[0]

    def update_modified(self, _id: int, modified: str):
        self._db.execute(
            """update playlist set modified = ?
               where user_id = ? and id = ?""",
            (modified, self._uid, _id)
        )

    def update_playlist_duration(self, _id: int):
        self._db.execute(
            """update playlist set duration = (
                 select sum(duration)
                 from track
                   inner join playlist_track on track_id = id
                 where user_id = ? and playlist_id = ?)
               where user_id = ? and id = ?""",
            (self._uid, _id, self._uid, _id)
        )

    def update_playlist_title(self, _id: int, title: str):
        self._db.execute(
            "update playlist set title = ? where user_id = ? and id = ?",
            (title, self._uid, _id)
        )

    def update_playlists_count(self, count: int):
        self._db.execute(
            "update user set playlists_count = ? where id = ?",
            (count, self._uid)
        )

    def update_tracks_count(self, _id: int):
        self._db.execute(
            """update playlist set tracks_count = (
                 select count(*)
                 from playlist_track
                 where user_id = ? and playlist_id = ?)
               where user_id = ? and id = ?""",
            (self._uid, _id, self._uid, _id)
        )

    def __get_ids(self, table: str):
        return [i[0] for i in self._db.select_all(f"select id from {table}")]

    def __get_params_with_uid(self, params: list):
        return [tuple([self._uid, *i]) for i in params]


class UserQuery(BaseQuery):
    def delete_user_data(self):
        self._db.execute("delete from user where id = ?", (self._uid,))

        self.delete_unused()

        self.user_name = None

    def get_genre_artists(self, genre):
        query = """select name
                   from artist
                   where id in (
                     select distinct at.artist_id
                     from artist_track at
                      inner join track t on t.id = at.track_id
                      inner join playlist_track pt on pt.track_id = t.id
                     where pt.user_id = ? and t.genre = ?)
                   order by name"""
        return self._db.select_all(query, (self._uid, genre))

    def get_user_artists(self):
        query = """select a.name, count(*) as col
                   from artist a
                     inner join artist_track at on at.artist_id = a.id
                     inner join playlist_track pt on pt.track_id = at.track_id
                   where pt.playlist_id = 3 and pt.user_id = ?
                   group by a.name
                   order by col desc, a.name"""
        return self._db.select_all(query, (self._uid,))

    def get_user_genres(self):
        query = """select genre, count(track.*) as col
                   from track
                     inner join playlist_track on track_id = id
                   where genre is not null and playlist_id = 3
                     and user_id = ?
                   group by genre
                   order by col desc, genre"""
        return self._db.select_all(query, (self._uid,))
