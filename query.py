from database import DataCtx


class BaseQuery:
    """Queries executing class."""
    def __init__(self):
        self._db = DataCtx()


class UserQuery(BaseQuery):
    def get_user_favorite(self, login):
        query = """select t.title
                    from track t 
                    inner join playlist_track pt on pt.track_id = t.id
                    inner join playlist p on p.user_id = pt.user_id and p.id = pt.playlist_id
                    inner join user u on u.id = p.user_id
                    where pt.playlist_id = 3 and u.login = ?
                    order by t.title
                    limit 20"""
        return self._db.select_all(query, (login,))

    def get_user_genres(self, login):
        query = """select t.genre, count(*) as col
                    from track t 
                    inner join playlist_track pt on pt.track_id = t.id
                    inner join playlist p on p.user_id = pt.user_id and p.id = pt.playlist_id
                    inner join user u on u.id = p.user_id
                    where t.genre is not null and pt.playlist_id = 3 and u.login = ?
                    group by t.genre
                    order by col desc, t.genre
                    limit 20"""
        return self._db.select_all(query, (login,))

    def get_user_artists(self, login):
        query = """select a.name, count(*) as col
                    from artist a
                    inner join artist_track at on at.artist_id = a.id
                    inner join track t on t.id = at.track_id
                    inner join playlist_track pt on pt.track_id = t.id
                    inner join playlist p on p.user_id = pt.user_id and p.id = pt.playlist_id
                    inner join user u on u.id = p.user_id
                    where pt.playlist_id = 3 and u.login = ?
                    group by a.name
                    order by col desc, a.name
                    limit 20"""
        return self._db.select_all(query, (login,))

    def get_genre_artists(self, login, genre):
        query = """select name
                    from artist
                    where id in
                    (select distinct at.artist_id
                        from artist_track at
                        inner join track t on t.id = at.track_id
                        inner join playlist_track pt on pt.track_id = t.id
                        inner join playlist p on p.user_id = pt.user_id and p.id = pt.playlist_id
                        inner join user u on u.id = p.user_id
                        where u.login = ? and t.genre = ? and pt.playlist_id = 3)
                    order by name"""
        return self._db.select_all(query, (login, genre))

    def get_user_playlists(self, login):
        query = """select p.*
                    from playlist p
                    inner join user u on u.id = p.user_id
                    where u.login = ?"""
        return self._db.select_all(query, (login,))


class Query(BaseQuery):
    def init_tables(self):
        self._db.execute_script(
            """PRAGMA foreign_keys=on;

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
                foreign key (user_id, playlist_id) references playlist(user_id, id) on delete cascade,
                foreign key (track_id) references track(id) on delete cascade);

            create table if not exists artist_track (
                artist_id integer,
                track_id integer,
                foreign key (artist_id) references artist(id) on delete cascade,
                foreign key (track_id) references track(id) on delete cascade);"""
        )

    def insert_user(self, *params):
        self._db.execute("insert into user values (?, ?, ?, ?)", tuple(params))

    def insert_playlists(self, params: list):
        self._db.execute_many(
            "insert into playlist values (?, ?, ?, ?, ?, ?)", params
        )

    def insert_tracks(self, params: list):
        self._db.execute_many(
            "insert into track values (?, ?, ?, ?, ?)", params
        )

    def insert_artists(self, params: list):
        self._db.execute_many("insert into artist values (?, ?)", params)

    def insert_playlist_tracks(self, params: list):
        self._db.execute_many(
            "insert into playlist_track values (?, ?, ?)", params
        )

    def insert_artist_track(self, params: list):
        self._db.execute_many(
            "insert into artist_track values (?, ?)", params
        )

    def get_uid(self, login: str):
        uid = self._db.select(
            "select id from user where login = ?", (login,)
        )
        return uid[0] if uid else None

    def get_tracks_ids(self):
        return self.__get_ids("track")

    def get_artists_ids(self):
        return self.__get_ids("artist")

    def get_playlists_ids(self, uid: int):
        return [
            i[0] for i in self._db.select_all(
                "select id from playlist where user_id = ?", (uid,)
            )
        ]

    def get_playlist_tracks_ids(self, uid: int, _id: int):
        return [
            i[0] for i in self._db.select_all(
                """select track_id from playlist_track 
                where user_id = ? and playlist_id = ?""",
                (uid, _id)
            )
        ]

    def get_playlist_title(self, uid: int, _id: int):
        return self._db.select(
            """select title from playlist
             where user_id = ? and id = ?""",
            (uid, _id)
        )[0]

    def get_modified(self, uid: int, _id: int):
        return self._db.select(
            """select modified from playlist
             where user_id = ? and id = ?""",
            (uid, _id)
        )[0]

    def update_playlist_title(self, uid: int, _id: int, title: str):
        self._db.execute(
            "update playlist set title = ? where user_id = ? and id = ?",
            (title, uid, _id)
        )

    def update_playlist_duration(self, uid: int, _id: int):
        self._db.execute(
            """update playlist set duration = (
                select sum(duration) 
                from track
                inner join playlist_track on track_id = id
                where user_id = ? and playlist_id = ?)
            where user_id = ? and id = ?""", (uid, _id, uid, _id)
        )

    def update_playlists_count(self, uid: int, count: int):
        self._db.execute(
            "update user set playlists_count = ? where id = ?",
            (count, uid)
        )

    def update_tracks_count(self, uid: int, _id: int):
        self._db.execute(
            """update playlist set tracks_count = (
                select count(*)
                from playlist_track
                where user_id = ? and playlist_id = ?)
            where user_id = ? and id = ?""", (uid, _id, uid, _id)
        )

    def update_modified(self, uid: int, _id: int, modified: str):
        self._db.execute(
            """update playlist set modified = ?
            where user_id = ? and id = ?""", (modified, uid, _id)
        )

    def delete_playlists(self, uid: int, ids: list):
        signs = ", ".join(["?"] * len(ids))
        self._db.execute(
            f"delete from playlist where id in ({signs}) and user_id = ?",
            (*ids, uid)
        )

    def delete_tracks(self, uid: int, kind: int, ids: list):
        signs = ", ".join(["?"] * len(ids))
        self._db.execute(
            f"""delete from playlist_track
            where track_id in ({signs}) 
            and user_id = ? and playlist_id = ?""",
            (ids, uid, kind)
        )

    def delete_unused(self):
        self.__delete_unused_tracks()
        self.__delete_unused_artists()

    def __delete_unused_tracks(self):
        self._db.execute(
            """delete from track
            where id not in (
                select track_id from playlist_track)"""
        )

    def __delete_unused_artists(self):
        self._db.execute(
            """delete from artist
            where id not in (
                select artist_id from artist_track)"""
        )

    def __get_ids(self, table: str):
        return [i[0] for i in self._db.select_all(f"select id from {table}")]
