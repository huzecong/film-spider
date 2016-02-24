# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
from datetime import datetime
from urlparse import urlparse
import movies.download as download


class JsonFileWriter:
    def __init__(self, path):
        print 'File writer:', path
        self.file = codecs.open(path, 'w', encoding='utf-8')
        self.first_item = True
        self.file.write("[\n")

    def write(self, text):
        if not self.first_item:
            self.file.write(",\n")
        else:
            self.first_item = False
        self.file.write(text)

    def close(self):
        self.file.write("\n]\n")
        self.file.close()


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.no_video_json = ''
        self.video_json = ''
        self.domains = []
        self.count = 0
        self.video_count = 0
        self.downloader = download.Downloader()

    def open_spider(self, spider):
        now = str(datetime.now()).split('.')[0].replace(' ', '_').replace(':', '.')
        self.no_video_json = JsonFileWriter(spider.name + '_movies_no_video_' + now + '.json')
        self.video_json = JsonFileWriter(spider.name + '_movies_with_video_' + now + '.json')

    def process_item(self, item, spider):
        self.count += 1
        if self.count % 30 == 0:
            print 'Done %d films' % self.count
        item['id'] = self.count
        line = json.dumps(dict(item), ensure_ascii=False)
        if 'videoURL' in item:
            self.video_json.write(line)
            domain = urlparse(item['videoURL']).netloc
            # self.downloader.download(item['title'], item['videoURL'], self.count)
            self.video_count += 1
            if domain not in self.domains:
                self.domains.append(domain)
        else:
            self.no_video_json.write(line)
        return item

    def close_spider(self, spider):
        print 'Total: %d films, %d of which contain videos' % (self.count, self.video_count)
        self.no_video_json.close()
        self.video_json.close()
        file = codecs.open('domains.txt', 'w', encoding='utf-8')
        for x in self.domains:
            file.write(x + '\n')
        file.close()
