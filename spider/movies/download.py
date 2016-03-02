from .multi_queue import MultitaskQueue
from .output import refresh, writeln, color
from functools import partial
import youtube_dl
from threading import Timer
import os
import time


class DownloadLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class Downloader:
    def __init__(self):
        self.queue = {}
        self.downloading = []
        self.multi = MultitaskQueue(self.start_download)
        self.status = 0
        Timer(0.5, self.print_progress).start()

    options = {
        # 'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        'format': 'worst',
        'logger': DownloadLogger()
    }

    running = False

    def start_download(self, dic):
        writeln('[' + color('INFO', 'blue') + '] Starting download of ' + dic['name']
                + ', saving as ID %d' % dic['id'])
        cur_option = self.options
        cur_option['progress_hooks'] = [partial(self.download_progress, dic['id'])]
        cur_option['outtmpl'] = 'video/' + str(dic['id']) + '/' + str(dic['id']) + r'.%(ext)s'
        downloader = youtube_dl.YoutubeDL(cur_option)
        try:
            downloader.download([dic['url']])
        except youtube_dl.DownloadError as e:
            writeln('[' + color('ERROR', 'red') + '] youtube_dl error: ' + e.message)

    _last_index = 0

    def print_progress(self):
        def _print_progress(index):
            rows, columns = map(int, os.popen('stty size', 'r').read().split())
            down_cnt, all_cnt = len(self.downloading), len(self.queue)
            if index >= down_cnt:
                index = 0

            dic = self.queue[self.downloading[index]]
            message = ''
            message += 'Job %d/%d' % (index + 1, down_cnt)
            if all_cnt > down_cnt:
                message += ' (%d pending)' % (all_cnt - down_cnt)
            message += ': ' + dic['name']

            eta = dic.get('eta', -1)
            if eta != -1:
                message += ' ETA: %ds' % eta
            speed = dic.get('speed', -1)
            if speed != -1:
                units = [('MB/s', 10 ** 6), ('KB/s', 10 ** 3)]
                unit = ('B/s', 1)
                for x in units:
                    if speed > x[1]:
                        unit = x
                        break
                message += ' Speed: %.1lf%s' % (speed / unit[1], unit[0])

            total, down = dic.get('total_bytes', -1), dic.get('downloaded_bytes', -1)
            if total != -1 and down != -1:
                message += ' Progress: %6.2lf%%' % (float(down) * 100 / float(total))

            length = columns - len(message)

            refresh(message)
            print message

        if len(self.downloading) > 0:
            _print_progress(self._last_index)
            self._last_index += 1
            if self._last_index >= len(self.downloading):
                self._last_index = 0
            self.running = True

        Timer(2, self.print_progress).start()

    def download_progress(self, id, dic):
        try:
            name = self.queue[id]['name']
        except KeyError:
            return

        if self.queue[id]['status'] == 'none':
            self.downloading.append(id)

        if dic['status'] == 'finished':
            message = 'Finished downloading %s. File saved to %s' % (name, dic['filename'])
            down = dic.get('downloaded_bytes', -1)
            if down != -1:
                message += ', size is %.1lfMB' % (float(down) / (10 ** 6))
            writeln('[' + color('INFO', 'blue') + '] ' + message)
            self.queue.pop(id)
            self.downloading.remove(id)
        elif dic['status'] == 'downloading':
            total = 0
            for x in ['total_bytes', 'total_bytes_estimate']:
                if dic[x] is not None:
                    total = dic[x]
                    break
            dic['total_bytes'] = total
            dic['name'] = name
            self.queue[id] = dic

    def download(self, name, url, id):
        self.queue[id] = {
            'name': name,
            'status': 'none'
        }
        self.multi.add({'name': name, 'url': url, 'id': id})
