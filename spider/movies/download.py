import os
import subprocess
import time
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
        
        self.FNULL = open(os.devnull, 'w')

    options = {
        'format': 'flv',
        'logger': DownloadLogger(),
    }

    def start_download(self, dic):
        writeln('[' + color('DOWN', 'cyan') + '] Starting download of %s from %s, saving as ID %d'
                % (dic['name'], dic['url'], dic['id']))
        # cur_option = self.options
        # cur_option['progress_hooks'] = [partial(self.download_progress, dic['id'])]
        # cur_option['outtmpl'] = 'video/' + str(dic['id']) + '/' + str(dic['id']) + r'.%(title)s-%(id)s.%(ext)s'
        # downloader = youtube_dl.YoutubeDL(cur_option)
        # try:
        #     downloader.download([dic['url']])
        #     self.download_progress(dic['id'], {'status': 'complete'})
        # except youtube_dl.DownloadError as e:
        #     writeln('[' + color('ERROR', 'red') + '] youtube_dl error for %s: ' % dic['name'] + e.message)
        #     self.download_progress(dic['id'], {'status': 'error'})
        self.download_progress(dic['id'], {'status': 'downloading'})
        outpath = 'video/' + str(dic['id']) + '/'
        try:
            os.makedirs(outpath)
        except:
            pass
        log = open(outpath + 'log.txt', 'w')
        subprocess.call(["you-get", "-o", outpath, dic['url']], stdout=log, stderr=subprocess.STDOUT)
        log.close()
        log = open(outpath + 'log.txt', 'r')
        if ' '.join(log.readlines()).find('error') != -1:
            self.download_progress(dic['id'], {'status': 'error'})
        else:
            self.download_progress(dic['id'], {'status': 'complete'})

    def print_progress(self):
        self.print_lock.acquire()

        down_cnt, all_cnt = len(self.downloading), len(self.queue)
        if down_cnt == 0:
            return

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
        message += color(': ' + dic['name'] + '  Part %d' % (dic['done_part'] + 1), 'green')

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

    REFRESH_TIME = 1

    def print_daemon(self):
        if len(self.downloading) > 0:
            with self.index.get_lock():
                self.index.value += 1
            self.print_progress()

        Timer(self.REFRESH_TIME, self.print_daemon).start()

    def download_progress(self, id, dic):
        self.print_lock.acquire()

        try:
            name = self.queue[id]['name']
            done_part = self.queue[id]['done_part']
        except KeyError:
            print 'KeyError'
            self.print_lock.release()
            return

        if self.queue[id]['status'] == 'none':
            self.downloading.append(id)

        dic['name'] = name
        dic['time'] = time.time()
        if dic['status'] in ['complete', 'error']:
            if dic['status'] == 'complete':
                message = 'All %d parts of %s downloaded' % (done_part, name)
                writeln(color('[DONE] ' + message, 'green'))
            else:
                message = 'Download of %s aborted due to error' % name
                writeln(color('[ABORT] ' + message, 'red'))
            self.downloading.remove(id)
            self.queue.pop(id)

        elif dic['status'] == 'finished':
            dic['done_part'] = done_part + 1
            message = 'Finished downloading part %d of %s. File saved to %s' \
                      % (dic['done_part'], name, dic['filename'])
            # message = 'Finished downloading part %d/%d of %s. File saved to %s' \
            #           % (dic['fragment_index'], dic['fragment_count'], name, dic['filename'])

            down = dic.get('downloaded_bytes', None)
            if down is not None:
                message += ', size is %.1lfMB' % (float(down) / (10 ** 6))
            writeln('[' + color('DOWN', 'green') + '] ' + message)
            self.queue[id] = dic

        elif dic['status'] == 'downloading':
            dic['done_part'] = done_part
            total = 0
            for x in ['total_bytes', 'total_bytes_estimate']:
                if x in dic and dic[x] is not None:
                    total = dic[x]
                    break
            dic['total_bytes'] = total
            self.queue[id] = dic

        self.print_lock.release()

        if dic['status'] == 'finished':
            self.print_progress()

    def download(self, name, url, id):
        self.queue[id] = {
            'name': name,
            'status': 'none',
            'time': time.time(),
            'done_part': 0,
        }
        self.multi.add({'name': name, 'url': url, 'id': id})
