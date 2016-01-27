import youtube_dl


class DownloadLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print msg


class Downloader:
    def __init__(self):
        self.queue = []
        self.status = 0

    def download_progress(self, dic):
        if dic['status'] == 'downloading':
            if self.status == 0:
                self.status = 1
                print 'Saving to %s' % dic['filename']
            message = ''
            total = 0
            for x in ['total_bytes', 'total_bytes_estimate']:
                if dic[x] is not None:
                    total = dic[x]
                    break
            if total != 0 and dic['downloaded_bytes'] is not None:
                message += '\tProgress: %6.2lf%%' % (float(dic['downloaded_bytes']) * 100 / total)
            if dic['eta'] is not None:
                message += '\tETA: %ds' % dic['eta']
            if dic['speed'] is not None:
                speed = dic['speed']
                units = [('MB/s', 10 ** 6), ('KB/s', 10 ** 3)]
                unit = ('B/s', 1)
                for x in units:
                    if speed > x[1]:
                        unit = x
                        break
                message += '\tSpeed: %.1lf%s' % (speed / unit[1], unit[0])

            if message != '':
                print message

        if dic['status'] == 'finished' and self.status == 1:
            message = 'Download finished. File saved to %s' % dic['filename']
            if dic['downloaded_bytes'] is not None:
                message += ', size is %.1lfMB' % (dic['downloaded_bytes'] / (10**6))
            print message
            self.status = 0
            try:
                movie = self.queue.pop()
                self.start_download(movie)
            except IndexError:
                pass

    def download(self, name, url, id):
        self.queue.append({'name': name, 'url': url, 'id': id})
        if self.status == 0:
            self.start_download(self.queue.pop())

    options = {
        'format': 'worst',
        'logger': DownloadLogger()
    }

    def start_download(self, dic):
        print 'Downloading %s from %s' % (dic['name'], dic['url'])
        cur_option = self.options
        cur_option['progress_hooks'] = [lambda x: self.download_progress(x)]
        cur_option['outtmpl'] = 'video/' + str(dic['id']) + r'.%(ext)s'
        downloader = youtube_dl.YoutubeDL(cur_option)
        try:
            downloader.download([dic['url']])
        except youtube_dl.DownloadError as e:
            pass
