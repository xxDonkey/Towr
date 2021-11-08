import sys
import os
from globals import *
from tokenizer import tokenize_src
from tparser import program_from_tokens
from com import com_program

def usage() -> None:
    """ Prints usage and exits with an exit code of 1. """
    print('python towr.py <SUBCOMMAND>')
    print('     sim     Simulates the program in Python')
    print('     com     Compiles the program')
    exit(1)

def main() -> None:
    if len(sys.argv) < 2:
        print('ERROR: Missing subcommand')
        usage()

    if len(sys.argv) < 3:
        print('ERROR: No file input')
        usage()

    filename = sys.argv[2]
    filepath = os.path.join(os.getcwd(), filename)
    code_body: str

    with open(filepath, 'r') as file:
        code_body = file.read()

    tokens = tokenize_src(TowrFile(code_body, filename))
    program = program_from_tokens(tokens)

    subcommand = sys.argv[1]
    if subcommand == 'sim':
        print(program)
    elif subcommand == 'com':
        com_program(program, filename.split('.')[0])
    else:
        print(f'ERROR: Subcommand {subcommand!r} not recognized')
        usage()

if __name__ == '__main__':
    main()