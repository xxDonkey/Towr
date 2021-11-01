import sys
import os
from enum import Enum, auto
from dataclasses import dataclass

class OperationType(Enum):
    PUSH_INT    = auto()
    PLUS        = auto()
    MULTIPLY    = auto()

class Operation:
    pass

@dataclass
class Program:
    operations: list[Operation]

def usage():
    """ Prints usage and exits with an exit code of 1. """
    print('python towr.py <SUBCOMMAND>')
    print('     sim     Simulates the program in Python')
    print('     com     Compiles the program')
    exit(1)

def main():
    if len(sys.argv) < 2:
        print('ERROR: Missing subcommand')
        usage()

    if len(sys.argv) < 3:
        print('ERROR: No file input')
        usage()

    filepath = os.path.join(os.path.dirname(__file__), sys.argv[2])
    print(filepath)

if __name__ == '__main__':
    main()