from typing import Union
from globals import *

def token_from_src(token: str, 
                   line: int, col: int, 
                   filename: str,
                   in_let: bool=False) -> Token:
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

    # TODO: improve iteration and token generation
    line, col = 0, -1
    prev_token: Token = Token.default_token()
    curr_token: str = ''
    for c in code_body:
        col += 1
        if (is_newline := c == '\n') or c == ' ':
            if is_newline:
                line += 1
                col = 0
            
            if curr_token:
                token = token_from_src(curr_token, line, col, filename, in_let=(prev_token.type == Keyword.LET))
                tokens.append(token)
                prev_token = token
                curr_token = ''

            continue
        curr_token += c
        
    if curr_token:
        token = token_from_src(curr_token, line, col, filename)
        tokens.append(token)

    return tokens

