from pyrail.utils.cli.clish import CliSh
from pyrail.utils.cli.shcmd import ShCmd
from pyrail.drivers.arduino.dccpp import DCCpp


class DCCppCli(CliSh):
    """DCC++ Command Line Interface"""

    def __init__(self):
        super(DCCppCli, self).__init__("dccpp")
        self.register_command(ThrottleCmd, "throttle", "t")
        self.register_command(PointCmd, "point", "p")
        self.register_command(LightCmd, "light")
        self.prompt = "dccpp>>> "
        self.dcc = None

    def define_argparser(self):
        parser = super(DCCppCli, self).define_argparser()
        # Define additional arguments for the DCCpp CLI
        parser.add_argument("-p", "--port", metavar="DEV",
                help="Serial port (default: %s)" % self.cfg.port)
        return parser

    def create(self, args):
        self.dcc = DCCpp(self.cfg.port)
        self.dcc.connect()

    def cleanup(self):
        self.dcc.disconnect()

    def do_info(self, line):
        """Print information about the current connected DCC++."""
        infos = "Connected:  %s\n" % self.dcc.connected
        if self.dcc.connected:
            infos += "Interface:  %s (%s)\n" % (self.dcc.port,
                    self.dcc.baudrate)
            self.dcc.status()
        self.stdout.write("%s" % infos)

    def do_on(self, line):
        """Turn on the main power for all tracks"""
        self.dcc.power_on()

    def do_off(self, line):
        """Turn off the main power for all tracks"""
        self.dcc.power_off()


    class Config(CliSh.Config):

        def __init__(self):
            super(DCCppCli.Config, self).__init__()
            self.port = "auto"

        def merge_args(self, args):
            super(DCCppCli.Config, self).merge_args(args)
            if args.port is not None:
                self.port = args.port


class ThrottleCmd(ShCmd):
    """Control the speed of a CAB"""

    def define_argparser(self):
        parser = super(ThrottleCmd, self).define_argparser()
        parser.add_argument("cab", metavar="CAB", type=int,
               help="Address of the engine decoder")
        parser.add_argument("speed", metavar="SPEED", type=int,
               help="Throttle speed from -126 to 126")
        return parser

    def run(self, session, line, args):
        self.shell.dcc.throttle(1, args.cab, args.speed)
        return True


class LightCmd(ShCmd):
    """Control the lights of a CAB"""

    def define_argparser(self):
        parser = super(LightCmd, self).define_argparser()
        parser.add_argument("cab", metavar="CAB", type=int,
               help="Address of the engine decoder")
        parser.add_argument("light", metavar="STATE", type=int,
               help="Light: 0: off, 1: on")
        return parser

    def run(self, session, line, args):
        fn = 128 if args.light == 0 else 144
        self.shell.dcc.function(args.cab, fn)
        return True

class PointCmd(ShCmd):
    """Control a point"""

    def define_argparser(self):
        parser = super(PointCmd, self).define_argparser()
        parser.add_argument("point", metavar="POINT", type=int,
               help="Address of the point")
        parser.add_argument("state", metavar="STATE", type=int,
               help="Point: 0: unthrown, 1: thrown")
        return parser

    def run(self, session, line, args):
        self.shell.dcc.turnout(args.point, args.state)
        return True


def main():
    cli = DCCppCli()
    cli.start()


### MAIN PROGRAM

if __name__ == "__main__":
    main()
