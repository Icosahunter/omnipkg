import shlex
import subprocess
import platform
import re
import string

provides_re = re.compile('\\(\\?P\\<(\\w*)\\>')

class Command:
    def __init__(self, cmd, parser=None, privileged=False, skip_lines=0):
        self.command = cmd
        self.parser = re.compile(parser) if parser else None
        self.privileged = privileged
        self.requires = [x[1] for x in string.Formatter().parse(cmd) if not x[1] in [None, '']]
        self.skip_lines = skip_lines
        self.provides = provides_re.findall(parser) if parser else []

    def __str__(self):
        return self.command

    def __call__(self, **kwargs):
        cmd = self.command
        if kwargs != None:
            cmd = cmd.format(**kwargs)
        if self.privileged and platform.system() == 'Linux':
            cmd = 'pkexec ' + cmd
        return self._run(cmd)

    def _run(self, cmd):
        capture_output = self.parser is not None
        print(cmd)
        result = subprocess.run(shlex.split(cmd), capture_output=capture_output).stdout
        if result is not None:
            return self._parse(result.decode('utf-8'))
        else:
            return []

    def _parse(self, text):

        if self.skip_lines > 0:
            _text = '\n'.join(text.split('\n')[self.skip_lines:-1]) + '\n'
        else:
            _text = text

        return [x.groupdict() for x in self.parser.finditer(_text)]
