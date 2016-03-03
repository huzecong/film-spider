# film-spider

Spiders crawling for film listing websites.

Currently supported:

- Youku: http://www.youku.com/v_olist/c_96.html
- M1905: http://www.1905.com/mdb/film/list/o0d0

## Usage

`youtube-dl` (https://github.com/rg3/youtube-dl) is required. First install by
``` shell
pip install youtube-dl
```
If requirements are satisfied, then
``` shell
git clone https://github.com/huzecong/film-spider
cd film-spider/spider
scrapy crawl youku -L ERROR # crawl for Youku
scrapy crawl m1905 -L ERROR # crawl for M1905
```

## Preferences

Preferences are currently hard-coded. Some preferences that you might be interested in are:

- **Download format**: In `download.py`, change `Downloader.options['format']`. Format should be legal `youtube-dl` format selection grammar (see https://github.com/rg3/youtube-dl#format-selection). Default is `'worst'`, standing for "worst quality (roughly 480P in the case of Youku)".
- **No. of download processes**: In `multi_queue.py`, change `MultitaskQueue.MAX_PROC`. Default is `4`.
- **Download path**: In `download.py`, find `Downloader.start_download` method, change `cur_option['outtmpl']`. Path should be legal `youtube-dl` output template grammar (see https://github.com/rg3/youtube-dl#output-template). Default is `'video/' + str(dic['id']) + '/' + str(dic['id']) + r'.%(ext)s'`, which will save the video to `video/<id>/<id>.<title>.<part>.<extension>`.

## Output format

Film info are written into three files:

- `<spider-name>_movies_no_video_<timestamp>.json`, containing JSON objects of videos **without** a video link.
- `<spider-name>_movies_video_<timestamp>.json`, containing JSON objects of videos **with** a video link.
- `domains.txt`, all of the domains in video links. (Only for M1905)

For the **M1905 spider**, JSON objects contain the following keys:

- `id`, parse counter as ID, corresponding to video filename.
- `link`, link to page on M1905.
- `title`, title of film.
- `titleEng`, English title of film (if available).
- `actors`, list of names of actors.
- `director`, list of names of directors.
- `boxOffice`, box office in CNY (if available).
- `genre`, list of genres (if available).
- `date`, release date in the format of "年月日" (YMD) (if available).
- `awards`, number of awards received (if available).
- `tags`, list of user-provided tags.
- `imageURL`, link to cover image.
- `videoURL`, link to video (if available).
 
  (If a list contains only one element, the list is flattened to a single element)

For the **Youku spider**, JSON objects contain the following keys:

- `id`, parse counter as ID, corresponding to video filename.
- `link`, link to page on Youku.
- `title`, title of film.
- `otherTitle`, aliases of the film (English names, etc.) (if available).
- `actors`, list of names of actors.
- `director`, list of names of directors.
- `genre`, list of genres (if available).
- `date`, release date in the format of "年月日" (YMD) (if available).
- `length`, length of the film in minutes.
- `description`, description of the film (if available).
- `region`, the region where the film was made (if available).
- `rating`, rating given by Youku users. Note that Youku pages also contain Douban ratings, but that information is not crawled by spider.
- `playCount`, number of times the film is played on Youku.
- `likeCount`, number of times the film is liked by Youku users.
- `commentCount`, number of comments of the film on Youku.
- `imageURL`, link to cover image.
- `videoURL`, link to video (if available).

If `videoURL` exists for a film, its worst-quality version is downloaded using `youtube-dl`. Video is saved to `video/<id>.<file format>`.

## Known issues

- Youku video parts are not concatenated.
- When downloading long videos on Youku, only a part could be downloaded. This issue is due to `youtube-dl` incompetence and I currently can do nothing about it.
