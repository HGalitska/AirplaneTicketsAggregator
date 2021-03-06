import subprocess
import threading
import time


class AirlinesInfoUpdater(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)

        self.name = name
        self.isWorking = True

    def run(self):
        print('Airlines Info Updater started')
        while self.isWorking:
            subprocess.run(['scrapy', 'crawl', 'airlines_info_spider'], cwd='scraping')
            time.sleep(60 * 60 * 24 * 3)

    def stop(self):
        self.isWorking = False
