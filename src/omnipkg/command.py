import shlex
import subprocess
import platform
import threading
from parse import parse
import string

class Command:
    def __init__(self, cmd, parser=None, privileged=False, skip_lines=0):
        self.command = cmd
        self.parser = parser
        self.privileged = privileged
        self.requires = [x[1] for x in string.Formatter().parse(cmd) if not x[1] in [None, '']]
        self.skip_lines = skip_lines
        if parser is not None:
            self.provides = [x[1] for x in string.Formatter().parse(parser) if not x[1] in [None, '']]
        else:
            self.provides = []
        #self.thread
    
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
            result = result.decode('utf-8')
        else:
            result = ''
        return self._parse(result)
    
    def _parse(self, text):
        result = []
        i = 0
        if self.skip_lines > 0:
            _text = '\n'.join(text.split('\n')[self.skip_lines:-1])
        else:
            _text = text
        while len(_text) > 0:
            parsed = parse(self.parser+'{end}', _text)
            if parsed is not None:
                i = parsed.spans['end'][0]
                _text = _text[i:]
                result.append(parsed.named)
                del result[-1]['end']
            else:
                parsed = parse(self.parser, _text)
                if parsed is not None:
                    result.append(parsed.named)
                break

        return result
