import logging
import shlex

from pyrail.utils.cli.cli import Cli
from pyrail.utils.cli.sh import Sh
from pyrail.exc.error import Error as pyrailError

_log = logging.getLogger(__name__)


class CliSh(Sh, Cli):

    def __init__(self, name=None):
        Cli.__init__(self, name)
        Sh.__init__(self, name)
        self.ignored_direct_cmds = ["help", "q", "quit", "exit", "last_ret",
                "logging"]

    def define_argparser(self):
        parser = super(CliSh, self).define_argparser()
        # Insert optional command and args arguments for direct calls
        parser.add_argument("cmd", nargs="?",
                choices=self.get_commands(self.ignored_direct_cmds),
                help="These are direct commands. If one is specified the %s "
                "is going the execute it and exit. Otherwise a line-oriented "
                "command interpreter is started." % self.name)
        parser.add_argument("cmd_args", nargs="...",
                help="Arguments of the command.")
        return parser

    def run(self, args):
        line = None
        if args.cmd is not None:
            # Perform direct calls from command line
            args_str = " ".join(map(shlex.quote, args.cmd_args))
            line = args.cmd + " " + args_str
            _log.debug("Execute: %s." % line)
        return self.invoke(line)

    def do_logging(self, line):
        """usage: logging [LOG-LEVEL]

        Get or set logging level

        When LOG-LEVEL is a valid log level (0-5) it will set it as new logging
        level, otherwise it prints the current logging level.
        """
        ret = False
        if line != None and len(line) > 0:
            try:
                log_level = int(line.split(":")[0])
                if self.check_log_level(log_level):
                    self.log_level = log_level
                    _log.debug("Set logging level to: %s" % self.log_level)
                    ret = True
                else:
                    raise ValueError("Logging level '%s' is not in range!" %
                            log_level)
            except ValueError as e:
                _log.error(e)
        else:
            self.stdout.write("%s:%s\n" % (self.log_level, self.log_level_name))
            ret = True
        return ret
