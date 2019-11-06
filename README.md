# YandexMusicParser

Using this project, you can get information about:
*  artists
*  genres
*  tracks count
*  total duration of all tracks

from your music library on the Yandex Music website. Only a login and a **public account** are required.

# Example

```python
  from YandexMusicParser.parser import MusicParser

  p = MusicParser(login="my_login")

  print(p.artists)
  # Counter({'Ludovico Einaudi': 25, 'Hans Zimmer': 22, 'Coldplay': 20, ...})
  
  print(p.genres)
  # Counter({'dance': 212, 'pop': 175, 'electronics': 115, ...})
  
  print(p.total_duration)
  # 34 h. 17 min. 36 sec.
  
  print(p.total_duration_ms)
  # 123456789
  
  print(p.tracks_count)
  # 567
```
