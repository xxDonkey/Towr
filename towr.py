import sys
import os
from enum import Enum, auto
from dataclasses import dataclass
from typing import Tuple, Union

class Keyword(Enum):
    LET         = auto()
    END         = auto()
    # IF          = auto()
    # FUNC        = auto()

class Intrinsic(Enum):
    PLUS        = auto()
    MULTIPLY    = auto()
    PRINT       = auto()
    SWAP        = auto()
    WRITE_MEM   = auto()
    RET_MEM     = auto()

class OperationType(Enum):
    PUSH_INT    = auto()
    KEYWORD     = auto()
    INTRINSIC   = auto()

class DataType(Enum):
    INT         = auto()
    BOOL        = auto()
    STRING      = auto()

Location = Tuple[str, int, int]

@dataclass
class Token:
    type: Union[Keyword, Intrinsic]
    operand: int
    location: Location
    
@dataclass
class Func:
    tokens: list[Token]
    location: Location

@dataclass
class Program:
    operations: list[Token, Func]
    operation_pointer: int = 0

@dataclass
class StackValue:
    datatype: DataType
    value: Union[int, bool, str]

KEYWORDS: dict[str, Keyword] = {
    'let'   : Keyword.LET,
    'end'   : Keyword.END,
}
assert len(KEYWORDS) == len(Keyword), 'Unassigned keywords'

INTRINSICS: dict[str, Intrinsic] = {
    '+'     : Intrinsic.PLUS,
    '*'     : Intrinsic.MULTIPLY,
    '^'     : Intrinsic.PRINT,
    '~'     : Intrinsic.SWAP,
    '!m'    : Intrinsic.WRITE_MEM, 
    '@m'    : Intrinsic.RET_MEM,
}
assert len(INTRINSICS) == len(Intrinsic), 'Unassigned intrinsics'

DATATYPES: dict[type, DataType] = {
    int     : DataType.INT,
    bool    : DataType.BOOL,
    str     : DataType.STRING,
}
assert len(DATATYPES) == len(DataType), 'Unassigned datatypes'

def load_variable_to_stack(stack: list[int], vars: dict[str, int], memory: list[bytearray], var_name: str, is_ref: bool=False) -> None:
    val: int
    if not is_ref:
        val_bytearr = memory[vars[var_name]]
        val = int.from_bytes(bytes(val_bytearr), 'big')
    else:
        val = vars[var_name]
    stack.append(val)

def parse_token(stack: list[int], vars: dict[str, int], memory: list[bytearray], tokens: list[str], token: str, i: int) -> int:
    ret_val: int = 1
    

    return ret_val

def simulate(code: str) -> None:
    program: Program = Program()
    stack: list[StackValue] = []


    
    stack: list[int] = []
    ptrs: dict[str, int] = {}
    memory: list[bytearray] = []

    tokens: list[str] = []

    line, col = 0, 0
    curr_token: str = ''
    for c in code:
        if c == ' ' or (is_newline := c == '\n'):
            if is_newline:
                line += 1
                col = 0
            
            if curr_token:
                tokens.append(curr_token)
                curr_token = ''
            continue
        curr_token += c
        col += 1
    if curr_token:
        tokens.append(curr_token)

    token_pointer = 0
    while token_pointer < len(tokens):
        token = tokens[token_pointer]
        token_pointer += parse_token(stack, ptrs, memory, tokens, token, token_pointer)
    


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

    filepath = os.path.join(os.path.dirname(__file__), sys.argv[2])
    towr_code: str
    with open(filepath, 'r') as file:
        towr_code = file.read()

    subcommand = sys.argv[1]
    if subcommand == 'sim':
        simulate(towr_code)
        # assert False, 'TODO: not implemented'
    elif subcommand == 'com':
        assert False, 'TODO: not implemented'
    else:
        print(f'ERROR: Subcommand {subcommand} not recognized')
        usage()

    

if __name__ == '__main__':
    main()