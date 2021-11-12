from typing import Union
from globals import *

def token_from_src(token: str, 
                   line: int, col: int, 
                   filename: str) -> Token:
    operation_type: Union[OperationType, None] = None
    keyword: Union[Keyword, None] = None
    intrinsic: Union[Intrinsic, None] = None
    operand: int = 0
    str_operand: str = ''

    if token in KEYWORDS:
        keyword = KEYWORDS[token]

    elif token in INTRINSICS:
        intrinsic = INTRINSICS[token]
    
    elif IS_INT(token):
        operation_type = OperationType.PUSH_INT
        operand = int(token)

    elif IS_BOOL(token):
        operation_type = OperationType.PUSH_BOOL
        bool_digit = int(token[:len(token) - 1])
        if not (-1 < bool_digit < 2):
            compiler_error((filename, line, col), 'Datatype `BOOL` cannot have a value other than 0 or 1', __file__)
        operand = bool_digit

    elif IS_STR(token):
        operation_type = OperationType.PUSH_STR
        str_operand = token[1:-1]

    else:
        operation_type = None

    types = [t for t in [operation_type, keyword, intrinsic] if t != None]
    type = None
    if len(types) > 0:
        type = types[0]

    return Token(
        type=type,
        operand=operand,
        str_operand=str_operand,
        location=(filename, line, col),
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
        start_str: bool = ch.startswith('"')
        end_str: bool = ch.startswith('"')

        if comment:
            in_comment = True

        if start_str:
            in_str = True
        
        if end_str:
            end_str = True
        
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
