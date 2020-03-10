# YandexMusicParser

## About
Using this project, you can get information about:
*  _User_: name, playlists list, playlists count
*  _Playlist_: title, tracks list, tracks count, duration, last modified datetime, artists counter, genres counter
*  _Track_: title, artists list, artists count, release year, genre, duration
*  _Artist_: name, tracks list, tracks count, genres, likes count

from your music library on the Yandex Music website. Only a login and a **public account** are required.

## Installation
- Clone the repo: <br>
  `git clone https://github.com/ElFanzo/YandexMusicParser.git`;
- Install Python >=3.6;
- Install pip;
- Install dependencies: <br>
  `pip install -r requirements.txt`

## Usage example

```python
  from yandex_music import Client

  me = Client(login="john_doe")
  # First, all the user's data will be saved in the database. 
  # After that, it'll be taken from the DB.
  # A user's data can be updated if neccessary -> me.update()
  
  user = me.user
  print(user.login)
  # john_doe
  
  print(user.name)
  # John Doe
  
  print(user)
  # User john_doe(John Doe, 3 playlist(s))
  
  first = user.playlists[0]
  print(first)
  # Playlist(Мне нравится, 1000 track(s))
  
  print(first.duration)
  # 70 h. 17 min. 36 sec.
  
  print(first.get_artists_counter())
  # {'Ludovico Einaudi': 25, 'Hans Zimmer': 22, 'Coldplay': 20, ...}
  
  track = first.tracks[123]
  print(track)
  # Rammstein - Mein Herz Brennt
  
  print(track.genre)
  # industrial
```
