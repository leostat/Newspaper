import os
import sys

if os.name == 'nt':
        ANSI = {
        # TODO : make it look nice on windows
                "white" : '',
                "purple" : '',
                "blue" : '',
                "green" : '',
                "yellow" : '',
                "red" : '',
                "bold" : '',
                "reset" : ''
        }
else:
        ANSI = {
                "white" : '\033[37m',
                "purple" : '\033[95m',
                "blue" : '\033[94m',
                "green" : '\033[92m',
                "yellow" : '\033[93m',
                "red" : '\033[91m',
                "bold" : '\033[1m',
                "reset" : '\033[0m'
        }

def debug(msg, override=False):
        print(ANSI["purple"] + ANSI["bold"] + "[DEBUG]: " + ANSI["reset"] + str(msg))

def fakedebug(msg):
        pass

def ok(msg):
        print(ANSI["green"] + ANSI["bold"] + "[OK]: " + ANSI["reset"] + msg)

def warn(msg):
        msg = ANSI["yellow"] + ANSI["bold"] + "[WARNING]: " + ANSI["reset"] + msg + "\n"
        sys.stderr.write(msg)

def err(msg, level="generic"):
        msg = ANSI["red"] + ANSI["bold"] + "[ERROR]: " + \
                ANSI["reset"] + msg + "\n"
        sys.stderr.write(msg)
        sys.exit(2)

