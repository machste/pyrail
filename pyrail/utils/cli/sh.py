from cmd import Cmd

from pyrail.utils.cli.shcmd import ShCmd


class Sh(Cmd, object):

    def __init__(self, name=None):
        Cmd.__init__(self)
        self.name = name
        self.exit_shell = False
        self.prompt = "%s>>> " % self.name
        self.parent_shell = None
        self.last_ret = None

    @property
    def root_shell(self):
        shell = self
        while shell.parent_shell is not None:
            shell = shell.parent_shell
        return shell

    @property
    def doc_leader(self):
        doc_text = ""
        if self.__doc__ != None:
            doc_text = "%s\n" % self.__doc__
        return doc_text

    def register_command(self, cmd_cls, name, nick=None):
        if not issubclass(cmd_cls, ShCmd):
            raise TypeError("Expected subclass of ShCmd!")
        cmd = cmd_cls(self, name)
        setattr(self, "help_%s" % cmd.name, cmd.print_help)
        setattr(self, "do_%s" % cmd.name, cmd.invoke)
        if nick is not None:
            setattr(self, "do_%s" % nick, cmd.invoke)        
        setattr(self, "abort_%s" % cmd.name, cmd.abort)

    def register_subshell(self, shell):
        if not isinstance(shell, Shell):
            raise TypeError("Expected instance of Shell!")
        setattr(self, "help_%s" % shell.name, shell.print_help)
        setattr(self, "do_%s" % shell.name, shell.invoke)
        shell.parent_shell = self

    def get_names(self):
        return dir(self)

    def get_commands(self, excludes=[]):
        cmds = []
        for cmd in self.completenames(""):
            if cmd not in excludes:
                cmds.append(cmd)
        return cmds

    def print_help(self):
        return self.do_help(None)

    def adopt_from_parent(self, parent_shell):
        pass

    def invoke(self, line):
        if self.parent_shell is not None:
            self.adopt_from_parent(self.parent_shell)
        if line is not None and len(line) > 0:
            if line.startswith("--help"):
                line = line[2:]
            line = self.precmd(line)
            ret = self.onecmd(line)
            self.postcmd(ret, line)
        else:
            self.cmdloop()
        return self.last_ret

    def preloop(self):
        self.exit_shell = False

    def emptyline(self):
        pass

    def onecmd(self, line):
        try:
            return Cmd.onecmd(self, line)
        except KeyboardInterrupt:
            cmd, arg, line = self.parseline(line)
            try:
                abort_func = getattr(self, "abort_" + cmd)
            except AttributeError:
                return False
            return abort_func()

    def postcmd(self, ret, line):
        # Interpret return value of None as True
        self.last_ret = ret if ret is not None else True
        return self.exit_shell

    def do_last_ret(self, line):
        """Print the return value of the last executed command"""
        self.stdout.write("%s\n" % self.last_ret)

    def do_exit(self, line):
        """Exit the current shell"""
        self.exit_shell = True

    def __str__(self):
        return str(self.parent_shell or self.name)

    # Shortcuts
    do_q = do_exit
    do_quit = do_exit
