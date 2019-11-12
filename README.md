# YandexMusicParser

Using this project, you can get information about:
*  user's name
*  artists
*  genres
*  tracks count
*  total duration of all tracks

from your music library on the Yandex Music website. Only a login and a **public account** are required.

# Usage example

```python
  from scraper import Listener

  me = Listener(login="john_doe")
  
  print(me.name)
  # John Doe
  
  print(me)
  # User john_doe(John Doe, 3 playlist(s))
  
  first = me.playlists[0]
  
  print(first)
  # Playlist(Мне нравится, 1000 track(s))

  print(first.artists)
  # {'Ludovico Einaudi': 25, 'Hans Zimmer': 22, 'Coldplay': 20, ...}
  
  print(first.artists["Kygo"])
  # 7
  
  print(first.genres)
  # {'dance': 212, 'pop': 175, 'electronics': 115, ...}
  
  print(first.genres["house"])
  # 50
  
  print(first.total_duration)
  # 70 h. 17 min. 36 sec.
  
  print(first.total_duration_ms)
  # 1234567890
  
  print(first.tracks_count)
  # 1000
```
