from multiprocessing import Lock, Manager
from sys import stdout


class Output:
    CLEAR_LINE = '\033[2K\r'
    RESET_CODE = '\033[0m'
    COLOR_CODE = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[94m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'gray': '\033[37m',
        'grey': '\033[37m'
    }

    lock = Lock()
    manager = Manager()
    last_refresh = ''

    @staticmethod
    def refresh(s):
        Output.lock.acquire()
        Output.last_refresh = s
        stdout.write(Output.CLEAR_LINE + s)
        stdout.flush()
        Output.lock.release()

    @staticmethod
    def writeln(s):
        Output.lock.acquire()
        stdout.write(Output.CLEAR_LINE + s + '\n' + Output.last_refresh)
        stdout.flush()
        Output.lock.release()

    @staticmethod
    def color(s, col):
        return Output.COLOR_CODE[col.lower()] + s + Output.RESET_CODE

    @staticmethod
    def length(s):
        ret = len(s.encode('utf-8'))
        ret -= 9 * (s.count('\033') // 2)
        return ret


refresh = Output.refresh
writeln = Output.writeln
color = Output.color
length = Output.length
