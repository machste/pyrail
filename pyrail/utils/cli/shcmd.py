import logging
import shlex

from argparse import ArgumentParser, RawDescriptionHelpFormatter
from inspect import cleandoc

from pyrail.exc.error import Error as pyrailError

_log = logging.getLogger(__name__)


class ShCmd(object):

    def __init__(self, shell, name):
        self.shell = shell
        self.name = name
        self.argparser = self.define_argparser()

    @property
    def stdin(self):
        return self.shell.stdin

    @property
    def stdout(self):
        return self.shell.stdout

    def define_argparser(self):
        parser = ArgumentParser(self.name, add_help=False,
                formatter_class=RawDescriptionHelpFormatter)
        parser.description = cleandoc(self.__doc__ or "No description!")
        parser.add_argument("-h", "--help", action="store_true",
                help="Show this help message")
        return parser

    def print_help(self):
        if self.argparser is not None:
            self.argparser.print_help()
        elif self.__doc__ is not None:
            self.stdout.write(cleandoc(self.__doc__))
        else:
            self.stdout.write("No help for command '%s'.\n" % self.name)

    def parse_args(self, line):
        try:
            args = shlex.split(line)
        except ValueError as e:
            _log.warn(str(e))
            args = None
        if self.argparser is not None:
            try:
                args = self.argparser.parse_args(args)
            except SystemExit:
                # Prevent parse_args function from exit, when it fails.
                args = None
        return args

    def pre_run(self, line, args):
        return self.shell

    def run(self, context, line, args):
        return True

    def post_run(self, ret, context, line, args):
        return ret

    def invoke(self, line):
        args = self.parse_args(line)
        if args is None:
            _log.debug("Parsing arguments failed.")
            return False
        # Check if user wants help, if so print help page and return
        if self.argparser is not None and args.help:
            self.argparser.print_help()
            return True
        # Run command 
        try:
            context = self.pre_run(line, args)
            ret = self.run(context, line, args)
            return self.post_run(ret, context, line, args)
        except ShCmd.Error as error:
            _log.error(error.message)
            return False

    def abort(self):
        return False


    class Error(pyrailError):
        pass


    class Fatal(pyrailError):
        pass
