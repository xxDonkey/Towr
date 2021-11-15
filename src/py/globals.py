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

class Keyword(Enum):
    LET         = auto()
    LETMEM      = auto()
    FUNC        = auto()
    IF          = auto()
    ELSE        = auto()
    ELSEIF      = auto()
    WHILE       = auto()
    DO          = auto()
    THEN        = auto()
    END         = auto()
    IMPORT      = auto()
    PARAMS      = auto()
    PARAMSPLIT  = auto()
    COUNTER     = auto()
    RESET       = auto()
    RETURN      = auto()
    RETURNNONE  = auto()

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
    READ        = auto()
    INC         = auto()
    DEC         = auto()
    STDOUT      = auto()
    STDERR      = auto()
    BYTE        = auto()
    AND         = auto()
    OR          = auto()
    XOR         = auto()
    NOT         = auto()

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
    rets: list[str]
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
    'then'  : Keyword.THEN,
    'func'  : Keyword.FUNC,
    'end'   : Keyword.END,
    'import': Keyword.IMPORT,
    'params': Keyword.PARAMS,
    '::'    : Keyword.PARAMSPLIT,
    'iota'  : Keyword.COUNTER,
    'rst'   : Keyword.RESET,
    'ret'   : Keyword.RETURN,
    'retnone': Keyword.RETURNNONE,
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
    '@'     : Intrinsic.READ,
    '++'    : Intrinsic.INC,
    '--'    : Intrinsic.DEC,
    'stdout': Intrinsic.STDOUT,
    'stderr': Intrinsic.STDERR,
    'sizeof_byte': Intrinsic.BYTE,
    '&&'    : Intrinsic.AND,
    '||'    : Intrinsic.OR,
    '^^'    : Intrinsic.XOR,
    '!'     : Intrinsic.NOT,
}
assert len(INTRINSICS) == len(Intrinsic), 'Unassigned intrinsics'

def CHECK_ASSIGNMENT(token: Token) -> None:
    """ Checks if a given token can be used as a variable or function name. """
    if token.value in KEYWORDS:
        compiler_error(token.location, 'Cannot use a keyword as a variable name', __file__)
    if token.value in INTRINSICS:
        compiler_error(token.location, 'Cannot use an intrinsic as a variable name', __file__)

    # TODO: check against other vars/funcs
