import logging


class ColourFormatter(logging.Formatter):

    def __init__(self, fmt=None, datefmt=None):
        super(ColourFormatter, self).__init__(fmt, datefmt)
        self.critical_color = "\x1b[48;5;1m%s\x1b[0m"
        self.error_color = "\x1b[38;5;1m%s\x1b[0m"
        self.warning_color = "\x1b[38;5;202m%s\x1b[0m"
        self.info_color = "\x1b[38;5;76m%s\x1b[0m"
        self.debug_color = "\x1b[38;5;8m%s\x1b[0m"

    @staticmethod
    def colourise(fmt_msg, ansi_wrapper):
        if ansi_wrapper != None:
            return ansi_wrapper % fmt_msg
        else:
            return fmt_msg

    def format(self, record):
        fmt_msg = super(ColourFormatter, self).format(record)
        if record.levelno <= logging.DEBUG:
            return self.colourise(fmt_msg, self.debug_color)
        elif record.levelno <= logging.INFO:
            return self.colourise(fmt_msg, self.info_color)
        elif record.levelno <= logging.WARNING:
            return self.colourise(fmt_msg, self.warning_color)
        elif record.levelno <= logging.ERROR:
            return self.colourise(fmt_msg, self.error_color)
        return self.colourise(fmt_msg, self.critical_color)
