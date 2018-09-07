import subprocess
import threading
import time


class AirlinesNewsUpdater(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)

        self.name = name
        self.isWorking = True

    def run(self):
        time.sleep(30)
        print('Airlines News Updater started')
        while self.isWorking:
            subprocess.check_output(['scrapy', 'crawl', 'airlines_news_spider'])

            time.sleep(60 * 60 * 3)

    def stop(self):
        self.isWorking = False
