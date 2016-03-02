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

    last_refresh = ''

    @staticmethod
    def refresh(s):
        stdout.write(Output.CLEAR_LINE + s)
        Output.last_refresh = s

    @staticmethod
    def writeln(s):
        stdout.write(Output.CLEAR_LINE + s + '\n')
        refresh(Output.last_refresh)

    @staticmethod
    def color(s, col):
        return Output.COLOR_CODE[col.lower()] + s + Output.RESET_CODE


refresh = Output.refresh
writeln = Output.writeln
color = Output.color
