

class variables:
    def __init__(self):
        self.bot = None
        self.sessions = {}
        self.threaddata = None
        self.threaddatalocker = None
        self.threaddialog = None
        self.threaddialoglocker = None
        self.threadtests = None
        self.threadtestslocker = None
        self.chartimgsAPI = 'https://quickchart.io/chart?c='
        self.threaddatalasttime = 0
        self.threadtesttime = 0

all = variables()
