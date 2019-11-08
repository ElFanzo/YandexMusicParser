# YandexMusicParser

Using this project, you can get information about:
*  artists
*  genres
*  tracks count
*  total duration of all tracks

from your music library on the Yandex Music website. Only a login and a **public account** are required.

# Usage example

```python
  from scraper import Listener

  listener = Listener(login="my_login")
  playlist = listener.playlist

  print(playlist.artists)
  # {'Ludovico Einaudi': 25, 'Hans Zimmer': 22, 'Coldplay': 20, ...}
  
  print(playlist.artists["Kygo"])
  # 7
  
  print(p.genres)
  # {'dance': 212, 'pop': 175, 'electronics': 115, ...}
  
  print(playlist.genres["house"])
  # 50
  
  print(p.total_duration)
  # 34 h. 17 min. 36 sec.
  
  print(p.total_duration_ms)
  # 123456789
  
  print(p.tracks_count)
  # 567
```
