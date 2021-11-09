from enum import Enum, auto
from typing import Tuple, Union
from dataclasses import dataclass

# (filename, line, col)
Location = Tuple[str, int, int]

# size, ptr
TStr = Tuple[int, int]

def __compiler_print(location: Location, type: str, message: str):
    f, l, c = location
    print(f'{f}:{l}:{c}: {type}: {message}')

def compiler_error(location: Location, message: str) -> None:
    __compiler_print(location, 'ERROR', message)
    exit(1)

def IS_INT(token: str) -> bool:
    return token.isdigit()

def IS_BOOL(token: str) -> bool:
    return token.endswith('b') and len(token) > 1 and token[:len(token) - 1].isdigit()

def IS_STR(token: str) -> bool:
    return token.startswith('"') and token.endswith('"')

class OperationType(Enum):
    PUSH_INT            = auto()
    PUSH_BOOL           = auto()
    PUSH_STR            = auto()
    VAR_REF             = auto()
    PUSH_STACK_SIZE     = auto()
    CHECK_STACK_SIZE_G  = auto()

class Keyword(Enum):
    LET         = auto()
    FUNC        = auto()
    IF          = auto()
    ELSE        = auto()
    ELSEIF      = auto()
    WHILE       = auto()
    DO          = auto()
    END         = auto()
    IMPORT      = auto()

class Intrinsic(Enum):
    PLUS        = auto()
    MINUS       = auto()
    MULTIPLY    = auto()
    PRINT       = auto()
    SWAP        = auto()
    EQUALS      = auto()
    GREATER     = auto()
    LESS        = auto()
    DUP         = auto()
    DROP        = auto()

class DataType(Enum):
    INT         = auto()
    BOOL        = auto()
    PTR         = auto()

@dataclass
class Token:
    type: Union[OperationType, Keyword, Intrinsic, None]
    operand: int
    str_operand: str
    location: Location
    value: str

    @classmethod
    def default_token(cls):
        return cls(type=None, operand=0, str_operand='', location=('', 0, 0), value='')

@dataclass
class Variable:
    name: str
    datatype: DataType
    value: int
    
@dataclass
class Operation:
    type: Union[OperationType, Keyword, Intrinsic]
    operand: Union[int, str]

@dataclass
class Func:
    operations: list[Operation]
    location: Location

@dataclass
class Program:
    operations: list[Operation]
    vars: list[Variable]
    funcs: list[Func]

    tokens: list[Token]
    
    def __str__(self) -> str:
        return f'{self.operations=}\n{self.vars=}\n{self.funcs=}'

@dataclass
class StackValue:
    datatype: DataType
    value: int

@dataclass
class TowrFile:
    code_body: str
    filename: str

KEYWORDS: dict[str, Keyword] = {
    'let'   : Keyword.LET,
    'if'    : Keyword.IF,
    'else'  : Keyword.ELSE,
    'elseif': Keyword.ELSEIF,
    'while' : Keyword.WHILE,
    'do'    : Keyword.DO,
    'func'  : Keyword.FUNC,
    'end'   : Keyword.END,
    'import': Keyword.IMPORT,
}
KEYWORDS_INV: dict[Keyword, str] = {v: k for k, v in KEYWORDS.items()}
assert len(KEYWORDS) == len(Keyword), 'Unassigned keywords'

INTRINSICS: dict[str, Intrinsic] = {
    '+'     : Intrinsic.PLUS,
    '-'     : Intrinsic.MINUS,
    '*'     : Intrinsic.MULTIPLY,
    '^'     : Intrinsic.PRINT,
    '~'     : Intrinsic.SWAP,
    '='     : Intrinsic.EQUALS,
    '>'     : Intrinsic.GREATER,
    '<'     : Intrinsic.LESS,
    'dup'   : Intrinsic.DUP,
    'drop'  : Intrinsic.DROP,
}
assert len(INTRINSICS) == len(Intrinsic), 'Unassigned intrinsics'

DATATYPES: dict[type, DataType] = {
    int     : DataType.INT,
    bool    : DataType.BOOL,
    str     : DataType.PTR,
}
assert len(DATATYPES) == len(DataType), 'Unassigned datatypes'

def CHECK_ASSIGNMENT(token: Token) -> None:
    """ Checks if a given token can be used as a variable or function name. """
    if token.value in KEYWORDS:
        compiler_error(token.location, 'Cannot use a keyword as a variable name')
    if token.value in INTRINSICS:
        compiler_error(token.location, 'Cannot use an intrinsic as a variable name')

    # TODO: check against other vars/funcs
