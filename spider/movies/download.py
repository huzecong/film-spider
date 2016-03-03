import os
from functools import partial
from multiprocessing import Manager, Lock, Value
from threading import Timer

import youtube_dl

from .multi_queue import MultitaskQueue
from .output import refresh, writeln, color, length


class DownloadLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class Downloader:
    def __init__(self):
        self.manager = Manager()
        self.queue = self.manager.dict()
        self.downloading = self.manager.list()
        self.index = Value('i', 0)
        self.print_lock = Lock()

        self.multi = MultitaskQueue(self.start_download)
        self.status = 0
        Timer(0.5, self.print_daemon).start()

    options = {
        'format': 'worst',
        'logger': DownloadLogger()
    }

    def start_download(self, dic):
        writeln('[' + color('DOWN', 'cyan') + '] Starting download of ' + dic['name'] +
                ', saving as ID %d' % dic['id'])
        cur_option = self.options
        cur_option['progress_hooks'] = [partial(self.download_progress, dic['id'])]
        cur_option['outtmpl'] = 'video/' + str(dic['id']) + '/' + str(dic['id']) + r'.%(title)s-%(id)s.%(ext)s'
        downloader = youtube_dl.YoutubeDL(cur_option)
        try:
            downloader.download([dic['url']])
        except youtube_dl.DownloadError as e:
            writeln('[' + color('ERROR', 'red') + '] youtube_dl error: ' + e.message)

    def print_progress(self):
        self.print_lock.acquire()

        down_cnt, all_cnt = len(self.downloading), len(self.queue)
        if down_cnt == 0:
            return
        index = 0
        with self.index.get_lock():
            index = self.index.value
            if index >= down_cnt:
                self.index.value = 0
                index = 0

        rows, columns = map(int, os.popen('stty size', 'r').read().split())

        dic = self.queue[self.downloading[index]]
        message = ''
        message += color('Job %d/%d' % (index + 1, down_cnt), 'green')
        if all_cnt > down_cnt:
            message += color(' (%d pending)' % (all_cnt - down_cnt), 'green')
        message += color(': ' + dic['name'], 'green')

        total, down = dic.get('total_bytes', None), dic.get('downloaded_bytes', None)
        if total is not None and down is not None:
            submessage = ' %6.2lf%%' % (float(down) * 100 / float(total))
            if length(message) + length(submessage) <= columns:
                message += submessage

        eta = dic.get('eta', None)
        if eta is not None:
            submessage = color('   ETA:', 'cyan') + ' %ds' % eta
            if length(message) + length(submessage) <= columns:
                message += submessage

        speed = dic.get('speed', None)
        if speed is not None:
            units = [('MB/s', 10 ** 6), ('KB/s', 10 ** 3)]
            unit = ('B/s', 1)
            for x in units:
                if speed > x[1]:
                    unit = x
                    break
            submessage = color('   Speed:', 'cyan') + ' %.1lf%s' % (speed / unit[1], unit[0])
            if length(message) + length(submessage) <= columns:
                message += submessage

        remain = columns - length(message)

        refresh(message)

        self.print_lock.release()

    def print_daemon(self):
        if len(self.downloading) > 0:
            with self.index.get_lock():
                self.index.value += 1
            self.print_progress()

        Timer(2, self.print_daemon).start()

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
            writeln('[' + color('DOWN', 'green') + '] ' + message)
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

        self.print_progress()

    def download(self, name, url, id):
        self.queue[id] = {
            'name': name,
            'status': 'none'
        }
        self.multi.add({'name': name, 'url': url, 'id': id})
