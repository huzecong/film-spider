# film-spider
Spiders crawling for film listing websites.

## Output format
Film info are written into three files:
- `movies_no_video_<timestamp>.json`, containing JSON objects of videos **without** a video link.
- `movies_video_<timestamp>.json`, containing JSON objects of videos **with** a video link.
- `domains.txt`, all of the domains in video links

JSON objects contain the following keys:
- `id`, parse counter as ID, corresponding to video filename.
- `link`, link to page on M1905.
- `title`, title of film.
- `titleEng`, English title of film (if available).
- `actors`, list of names of actors.
- `director`, list of names of directors.
- `boxOffice`, box office in CNY (if available).
- `genre`, list of genres (if available).
- `date`, release date in format of "年月日" (YMD) (if available).
- `awards`, number of awards received (if available).
- `tags`, list of user-provided tags.
- `imageURL`, link to cover image.
- `videoURL`, link to video (if available).
(If a list contains only one element, the list is flattened to a single element)

If `videoURL` exists for a film, its worst-quality version is downloaded using `youtube-dl`. Video is saved to `video/<id>.<file format>`.

## TODO
- Implement parallel downloading mechanism.
- Optimize console output.
- Concatenate downloaded videos (issue confirmed for Youku videos)
