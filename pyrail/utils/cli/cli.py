import logging

from argparse import (ArgumentParser, RawDescriptionHelpFormatter, FileType,
        ArgumentTypeError)
from inspect import cleandoc

from pyrail import __version__
from pyrail.utils.log.formatter import ColourFormatter
from pyrail.exc.error import Error as pyrailError

_log = logging.getLogger(__name__)


class Cli(object):
    """Command Line Interface Base Class"""

    LOG_LEVELS = { 0: None, 1: logging.CRITICAL, 2: logging.CRITICAL,
            3: logging.ERROR, 4: logging.WARNING, 5: logging.INFO,
            6: logging.INFO, 7: logging.DEBUG
    }

    EXIT_SUCCESS = 0
    EXIT_FAILURE = 1

    def __init__(self, name=None):
        self.name = name or self.__class__.__name__
        self.version = __version__
        self.logger = logging.getLogger()
        self.cfg = self.Config()

    @property
    def log_level(self):
        for sys_lvl, py_lvl in self.LOG_LEVELS.items():
            if py_lvl == self.logger.level:
                return sys_lvl
        return -1

    @classmethod
    def validate_log_level(cls, level):
        return level in cls.LOG_LEVELS

    @log_level.setter
    def log_level(self, level):
        if self.validate_log_level(level):
            py_lvl = self.LOG_LEVELS[level]
            if py_lvl is not None:
                self.logger.propagate = True
                self.logger.setLevel(self.LOG_LEVELS[level])
            else:
                self.logger.propagate = False

    @property
    def log_level_name(self):
        return logging.getLevelName(self.logger.level)

    @classmethod
    def check_log_level(cls, level):
        level = int(level)
        if level not in cls.LOG_LEVELS:
            msg = "Log level must be between 0..%i" % len(cls.LOG_LEVELS)
            raise ArgumentTypeError(msg)
        return level

    def define_argparser(self):
        parser = ArgumentParser(formatter_class=RawDescriptionHelpFormatter,
                description=cleandoc(self.__doc__))
        parser.add_argument("-l", "--log-level", dest="log_level",
                type=self.check_log_level,
                help="Log level 0-7 (RFC 5424, syslog)")
        parser.add_argument("-c", "--config-file", metavar="FILE",
                dest="cfg_file", type=FileType("r"), help="Configuration FILE")
        return parser

    def parse_args(self):
        parser = self.define_argparser()
        return parser.parse_args()

    def setup_logging(self):
        log_console = logging.StreamHandler()
        log_console.setFormatter(ColourFormatter(self.cfg.log_format))
        self.logger.addHandler(log_console)
        self.log_level = self.cfg.log_level
        _log.info("%s - %s" % (self.name, self.version))

    def create(self, args):
        pass

    def run(self, args):
        return True

    def abort(self):
        _log.warn("Aborting ...")
        return Cli.EXIT_FAILURE

    def cleanup(self):
        pass

    def start(self):
        exit_code = 1
        args = self.parse_args()
        self.cfg.load_from_file(args.cfg_file)
        self.cfg.merge_args(args)
        self.setup_logging()
        try:
            self.create(args)
            try:
                if self.run(args):
                    exit_code = Cli.EXIT_SUCCESS
                else:
                    exit_code = Cli.EXIT_FAILURE
            except Cli.Error as e:
                _log.error(e)
            except Cli.Exit as e:
                _log.log(e.log_level, e)
                exit_code = e.exit_code
            except KeyboardInterrupt:
                exit_code = self.abort()
            finally:
                self.cleanup()
        except pyrailError as e:
            _log.error(e)
        exit(exit_code)


    class Config(object):

        def __init__(self):
            self.log_level = 4
            self.log_format = "%(name)s %(levelname)s: %(message)s"

        def load_from_file(self, file_name):
            pass

        def merge_args(self, args):
            if args.log_level is not None:
                self.log_level = args.log_level


    class Error(pyrailError):
        pass


    class Exit(pyrailError):

        def __init__(self, exit_code, message=None):
            super(Cli.Exit, self).__init__(message)
            self.exit_code = exit_code

        @property
        def log_level(self):
            return logging.INFO if self.is_normal() else logging.ERROR

        def is_normal(self):
            return self.exit_code == Cli.EXIT_SUCCESS

        def __str__(self):
            if self.is_normal():
                _msg = "" if self.message == None else "(%s)" % self.message
                _str = "Exiting normally %s..." % _msg
            else:
                _str = "%s Exiting ... (code %s)" % (self.message,
                        self.exit_code)
            return _str


    class Fatal(Exit):

        def __init__(self, message, exit_code=None):
            exit_code = exit_code or Cli.EXIT_FAILURE
            super(Cli.Fatal, self).__init__(exit_code, message)
