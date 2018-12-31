
__version__ = '0.1.1'

default_color = dict(
                bg = '#fff',
                line = '#efae7c',
                logo = '#f9f1c0'
            )

class AN_Module():
    def __init__(self, name, version, color = default_color):
        self.moduleName = name
        self.__version__ = version
        self.color = color
        self.state = 'running'
    def isRunning(origin_func):
        def wrapper(self, *args, **kwargs):
            if self.state.upper() == 'RUNNING':
                return origin_func(self, *args, **kwargs)
            return False
        return wrapper
    @isRunning
    def isrunning(self):
        return True
    def module_close(self):
        self.state = 'stopped'
    def module_open(self, opt = True):
        if opt:
            self.state = 'running'
            return True
        self.state = 'Running'
        return True
    def getinfo(self):
        return dict(
            name = self.moduleName,
            ver = self.__version__,
            colors = self.color,
            state = self.state,
        )