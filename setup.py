# coding: utf-8
from __future__ import print_function
import os
import sys
from subprocess import Popen, PIPE, STDOUT
from threading import Timer

from config import Config

COMMANDS = '''\
\\cp -f %(APP_SRV_FILE)s /usr/lib/systemd/system/
systemctl daemon-reload
systemctl enable %(APP_SRV_FILE)s
systemctl restart %(APP_SRV_FILE)s
systemctl status %(APP_SRV_FILE)s
''' % Config.to_dict()

def execute_command(cmd, timeout=30):
    '''
    execute command line
    return: errcode:int, outputs:string
    '''
    proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    timer = Timer(timeout, proc.kill)

    outs = ''
    try:
        timer.start()
        outs, __ = proc.communicate()
    finally:
        timer.cancel()
        errcode = proc.returncode

    return errcode, outs


def main():
    for cmd in COMMANDS.strip().splitlines():
        print(cmd)
        ret, outs = execute_command(cmd)
        if outs: print(outs.decode())
        if ret != 0: return ret
    return 0


if __name__ == '__main__':
    sys.exit(int(main() or 0))
