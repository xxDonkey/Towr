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
    EQUALS      = auto()
    GREATER     = auto()
    LESS        = auto()

class OperationType(Enum):
    PUSH_INT    = auto()
    PUSH_BOOL   = auto()
    PUSH_STR    = auto()
    KEYWORD     = auto()
    INTRINSIC   = auto()

class DataType(Enum):
    INT         = auto()
    BOOL        = auto()
    STR         = auto()

# (filename, line, col)
Location = Tuple[str, int, int]

@dataclass
class Token:
    type: OperationType
    keyword: Union[Keyword, None]
    intrinsic: Union[Intrinsic, None]
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

@dataclass
class TowrFile:
    code_body: str
    filename: str

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
    '='     : Intrinsic.EQUALS,
    '>'     : Intrinsic.GREATER,
    '<'     : Intrinsic.LESS,
}
assert len(INTRINSICS) == len(Intrinsic), 'Unassigned intrinsics'

DATATYPES: dict[type, DataType] = {
    int     : DataType.INT,
    bool    : DataType.BOOL,
    str     : DataType.STR,
}
assert len(DATATYPES) == len(DataType), 'Unassigned datatypes'

def sim_program(program: Program) -> None:
    op: int = program.operation_pointer
    ops: list[Token, Func] = program.operations
    stack: list[StackValue] = []

    while op < len(ops):
        operation = ops[op]

        if isinstance(operation, Token):
            if operation.type == OperationType.KEYWORD:
                assert False, '`Keywords` not implemented'

            elif operation.type == OperationType.INTRINSIC:
                if operation.intrinsic == Intrinsic.PLUS:
                    pass
                assert False, '`Intrinsics` not implemented'

            else:
                assert len(OperationType) == 5, 'Unhandled elements of `OperationType`'
                if operation.type == OperationType.PUSH_INT:
                    pass
                elif operation.type == OperationType.PUSH_BOOL:
                    pass
                elif operation.type == OperationType.PUSH_STR:
                    pass

        elif isinstance(operation, Func):
            assert False, '`Funcs` not implemented'

        op += 1
    

def token_from_string(token: str, line: int, col: int, filename: str):
    operation_type: Union[OperationType, None] = None
    operand: int = 0
    keyword: Union[Keyword, None] = None
    intrinsic: Union[Intrinsic, None] = None

    if token in KEYWORDS:
        operation_type = OperationType.KEYWORD
        keyword = KEYWORDS[token]

    elif token in INTRINSICS:
        operation_type = OperationType.INTRINSIC
        intrinsic = INTRINSICS[token]
    
    elif token.isdigit():
        operation_type = OperationType.PUSH_INT
        operand = int(token)

    else:
        assert False, f'Unknown token {token!r}'

    return Token(
        type=operation_type,
        keyword=keyword,
        intrinsic=intrinsic,
        operand=operand,
        location=(filename, line, col)
    )

def parse_to_program(file: TowrFile) -> Program:
    code_body: str = file.code_body
    filename: str = file.filename
    tokens: list[Token] = []

    line, col = 0, -1
    curr_token: str = ''
    for c in code_body:
        col += 1
        if c == ' ' or (is_newline := c == '\n'):
            if is_newline:
                line += 1
                col = 0
            
            if curr_token:
                token = token_from_string(curr_token, line, col, filename)
                tokens.append(token)
                curr_token = ''

            continue
        curr_token += c
    if curr_token:
        token = token_from_string(curr_token, line, col, filename)
        tokens.append(token)

    # TODO: function interpretation, let interpretation

    program: Program = Program(operations=tokens)
    return program

    


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
    filepath = os.path.join(os.path.dirname(__file__), sys.argv[2])
    code_body: str
    with open(filepath, 'r') as file:
        code_body = file.read()

    subcommand = sys.argv[1]
    if subcommand == 'sim':
        program = parse_to_program(TowrFile(code_body, filename))
        sim_program(program)
    elif subcommand == 'com':
        assert False, 'TODO: not implemented'
    else:
        print(f'ERROR: Subcommand {subcommand} not recognized')
        usage()

    

if __name__ == '__main__':
    main()