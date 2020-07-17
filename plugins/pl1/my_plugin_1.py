from .. import base
from .test import kek
import time


class pluginClass1(base.Plugin):
    progress = -1

    def textAnalysis(self, text, options):
        while self.progress < 100:
            self.progress += 8
            time.sleep(3)
        return kek.print1()
