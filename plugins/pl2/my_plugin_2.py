from .. import base
import time


class plugin2(base.Plugin):
    progress = 0
    opt = ""

    def textAnalysis(self, text, options):
        self.opt = options
        while self.progress < 100:
            self.progress += 30
            time.sleep(3)
        return [[[0, 1], [2, 4]], [[5, 7]]]

    def getStatistics(self):
        return "lolkek \n" + self.opt

    def getProgress(self):
        return self.progress
