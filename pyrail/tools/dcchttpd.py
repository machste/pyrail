import logging
import json

from http.server import HTTPServer, HTTPStatus, BaseHTTPRequestHandler

from pyrail.utils.cli.cli import Cli
from pyrail.drivers.arduino.dccpp import DCCpp
from pyrail.exc.error import Error

_log = logging.getLogger(__name__)


class DccHTTPRequestHandler(BaseHTTPRequestHandler):

    def command_handler(self, request):
        cmd = None
        args = []
        # Parse path
        parts = self.path.split("/")
        for part in parts:
            if len(part) <= 0:
                continue
            if cmd is None:
                cmd = part
            else:
                args.append(part)
        _log.debug("command: %s, args: %s" % (cmd, " ".join(args)))
        if cmd is None:
            raise DccHttpdRequestError("No command defined!")
        # Lookup command
        dcc_cmd_cb = getattr(self.server.main, "do_%s" % cmd, None)
        if not callable(dcc_cmd_cb):
            raise DccHttpdRequestError("Command '%s' not found!" % cmd)
        # Execute command
        response = {}
        response["status"] = dcc_cmd_cb(args, response)
        return response

    def do_GET(self):
        try:
            response = self.command_handler(None)
        except DccHttpdRequestError as err:
            self.send_error(HTTPStatus.NOT_FOUND, err.message)
            return
        json_data = bytes(json.dumps(response), "utf-8")        
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=UTF-8")
        self.send_header("Content-Length", str(len(json_data)))
        self.end_headers()
        self.wfile.write(json_data)


class DccHttpd(Cli):
    """HTTP Server for DCC Commands"""

    def __init__(self):
        super(DccHttpd, self).__init__("dcchttpd")
        self.dcc = None
        self.httpd = None

    def define_argparser(self):
        parser = super(DccHttpd, self).define_argparser()
        # Define additional arguments for the DCCpp CLI
        parser.add_argument("-p", "--port", metavar="DEV",
                help="Serial port (default: %s)" % self.cfg.port)
        return parser

    def create(self, args):
        self.dcc = DCCpp(self.cfg.port)
        if not self.dcc.connect():
            raise Error("Unable to connect to DCC++ station!")
        self.httpd = HTTPServer(('', 8080), DccHTTPRequestHandler)
        self.httpd.main = self

    def run(self, args):
        self.httpd.serve_forever()

    def cleanup(self):
        self.dcc.disconnect()

    def do_power(self, args, response):
        ret = False
        if len(args) == 0:
            response["power"] = "unknown"
        else:
            power_state = args[0].lower()
            if power_state in ("1", "true", "on"):
                ret = self.dcc.power_on()
            else:
                ret = self.dcc.power_off()        
        return ret

    def do_point(self, args, response):
        if len(args) != 2:
            response["error"] = "Invalid number of arguments!"
            return False
        # Parse point address
        try:
            point = int(args[0])
        except ValueError:
            response["error"] = "Invalid point address '%s'!" % args[0]
            return False
        # Parse position of point
        try:
            position = int(args[1])
        except ValueError:
            response["error"] = "Invalid position argument '%s'!" % args[1]
            return False
        if not position in (0, 1):
            response["error"] = "Position must be 0 or 1!"
            return False
        return self.dcc.turnout(point, position)


    class Config(Cli.Config):

        def __init__(self):
            super(DccHttpd.Config, self).__init__()
            self.port = "auto"

        def merge_args(self, args):
            super(DccHttpd.Config, self).merge_args(args)
            if args.port is not None:
                self.port = args.port


class DccHttpdRequestError(Error):
    pass


def main():
    dcchttpd = DccHttpd()
    dcchttpd.start()

### MAIN PROGRAM

if __name__ == "__main__":
    main()
