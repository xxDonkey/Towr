from enum import Enum, auto
from typing import Any, Tuple, Union
from dataclasses import dataclass, field

# (filename, line, col)
Location = Tuple[str, int, int]

# size, ptr
TStr = Tuple[int, int]

COMMENT = '#'

def __compiler_print(location: Location, type: str, message: str):
    f, l, c = location
    print(f'{f}:{l}:{c}: {type}: {message}')

def compiler_error(location: Location, message: str, py_file: str) -> None:
    print(f'Error in {py_file} ...')
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
    PUSH_VAR_REF        = auto()
    FUNC_CALL           = auto()
    WRITE_STACK_SIZE    = auto()
    PUSH_STACK_SIZE     = auto()
    RETURN              = auto()

class Keyword(Enum):
    LET         = auto()
    LETMEM      = auto()
    FUNC        = auto()
    IF          = auto()
    ELSE        = auto()
    ELSEIF      = auto()
    WHILE       = auto()
    DO          = auto()
    END         = auto()
    IMPORT      = auto()
    PARAMS      = auto()

class Intrinsic(Enum):
    PLUS        = auto()
    MINUS       = auto()
    MULTIPLY    = auto()
    DIVMOD      = auto()
    PRINT       = auto()
    SWAP        = auto()
    EQUALS      = auto()
    GREATER     = auto()
    LESS        = auto()
    DUP         = auto()
    DROP        = auto()
    STORE       = auto()
    INC         = auto()
    DEC         = auto()

class DataType(Enum):
    INT         = auto()
    BOOL        = auto()
    PTR         = auto()
    LIST        = auto()

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
    value: int
    malloc: bool = False
    
@dataclass
class Operation:
    type: Union[OperationType, Keyword, Intrinsic]
    operand: Union[int, str]
    args: list[Any] = field(default_factory=list)

@dataclass
class Func:
    name: str
    params: list[str]
    operations: list[Operation]
    vars: list[Variable]
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
    'letmem': Keyword.LETMEM,
    'if'    : Keyword.IF,
    'else'  : Keyword.ELSE,
    'elseif': Keyword.ELSEIF,
    'while' : Keyword.WHILE,
    'do'    : Keyword.DO,
    'func'  : Keyword.FUNC,
    'end'   : Keyword.END,
    'import': Keyword.IMPORT,
    'params': Keyword.PARAMS,
}
KEYWORDS_INV: dict[Keyword, str] = {v: k for k, v in KEYWORDS.items()}
assert len(KEYWORDS) == len(Keyword), 'Unassigned keywords'

INTRINSICS: dict[str, Intrinsic] = {
    '+'     : Intrinsic.PLUS,
    '-'     : Intrinsic.MINUS,
    '*'     : Intrinsic.MULTIPLY,
    '/'     : Intrinsic.DIVMOD,
    '^'     : Intrinsic.PRINT,
    '~'     : Intrinsic.SWAP,
    '=='    : Intrinsic.EQUALS,
    '>'     : Intrinsic.GREATER,
    '<'     : Intrinsic.LESS,
    'dup'   : Intrinsic.DUP,
    'drop'  : Intrinsic.DROP,
    '='     : Intrinsic.STORE,
    '++'    : Intrinsic.INC,
    '--'    : Intrinsic.DEC,
}
assert len(INTRINSICS) == len(Intrinsic), 'Unassigned intrinsics'

def CHECK_ASSIGNMENT(token: Token) -> None:
    """ Checks if a given token can be used as a variable or function name. """
    if token.value in KEYWORDS:
        compiler_error(token.location, 'Cannot use a keyword as a variable name', __file__)
    if token.value in INTRINSICS:
        compiler_error(token.location, 'Cannot use an intrinsic as a variable name', __file__)

    # TODO: check against other vars/funcs
