from typing import Union
from globals import *

def token_from_src(token: str, 
                   line: int, col: int, 
                   filename: str) -> Token:
    _type: Union[OperationType, Keyword, Intrinsic, None] = None
    operand: int = 0
    str_operand: str = ''
    location = (filename, line, col)

    match list(token):
        case [*chs] if (Str := ''.join(chs)) in KEYWORDS:
            _type = KEYWORDS[Str]

        case [*chs] if (Str := ''.join(chs)) in INTRINSICS:
            _type = INTRINSICS[Str]

        case ['-', *chs] | [*chs] if IS_INT(''.join(chs)):
            _type = OperationType.PUSH_INT
            operand = int(token)

        # not used right now, will be with more types for memory saving
        case [val, 'b'] if val.isdigit() and 0 <= (val_int := int(val)) <= 1:
            _type = OperationType.PUSH_BOOL
            operand = val_int

        case ['"', *chs, '"']:
            _type = OperationType.PUSH_STR
            str_operand = ''.join(chs)

    return Token(
        type=_type,
        operand=operand,
        str_operand=str_operand,
        location=location,
        value=token
    )

def tokenize_src(file: TowrFile) -> list[Token]:
    code_body: str = file.code_body
    filename: str = file.filename
    tokens: list[Token] = []

    endswith_newline = code_body.endswith('\n')
    endswith_space = code_body.endswith(' ')
    if not endswith_newline and not endswith_space :
        compiler_error((filename, 1, 1), 'Space or newline requireed at EOF', __file__)

    # TODO: improve iteration and token generation
    line, col = 1, 1
    ctoken: str = ''
    in_str: bool = False
    in_comment: bool = False

    for ch in code_body:
        newline: bool = (ch == '\n')
        space: bool = (ch == ' ')
        comment: bool = (ch == COMMENT)
        is_str: bool = (ch == '"')

        if comment:
            in_comment = True

        if is_str:
            in_str = not in_str
        
        if (not newline and not space and not in_comment) or (not newline and in_str):
            ctoken += ch
        
        if newline:
            if ctoken:
                tokens.append(token_from_src(ctoken, line, col, filename))
                ctoken = ''
            line += 1
            col = 1
            in_comment = False
        elif space and not in_str:
            if ctoken:
                tokens.append(token_from_src(ctoken, line, col, filename))
                ctoken = ''
            col += 1
        else:
            col += 1

    return tokens
