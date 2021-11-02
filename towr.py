import sys
import os
from enum import Enum, auto
from dataclasses import dataclass
from typing import Union

class Keyword(Enum):
    LET         = auto()
    END         = auto()
    # IF          = auto()
    # FUNC        = auto()

class Intrinsic(Enum):
    pass

class OperationType(Enum):
    PUSH_INT    = auto()
    PLUS        = auto()
    MULTIPLY    = auto()
    PRINT       = auto()
    SWAP        = auto()
    WRITE_MEM   = auto()
    RET_MEM     = auto()

    NO_OP       = auto()

@dataclass
class Operation:
    type: OperationType
    operand: int

@dataclass
class Func:
    func_body: str

KEYWORDS: dict[str, Keyword] = {
    'let': Keyword.LET,
    'end': Keyword.END,
}
assert len(KEYWORDS) == len(Keyword), 'Unassigned keywords'

INTRINSICS: dict[str, Intrinsic] = {

}
assert len(INTRINSICS) == len(Intrinsic), 'Unassigned intrinsics'

OPERATION_CONVERTER = {
    'funcs': {
        'isdigit'   : OperationType.PUSH_INT,
    },
    'direct': {
        '+'         : OperationType.PLUS,
        '*'         : OperationType.MULTIPLY,
        '^'         : OperationType.PRINT,
        '~'         : OperationType.SWAP,
        '!m'        : OperationType.WRITE_MEM, 
        '@m'        : OperationType.RET_MEM,
    },
}

def in_converter(token: str) -> Union[Operation, None]:
    if token in OPERATION_CONVERTER['direct']:
        return Operation(
            type=OPERATION_CONVERTER['direct'][token],
            operand=0
        )

    for condition in OPERATION_CONVERTER['funcs']:
        condition_func = getattr(token, condition)
        if condition_func():
            return Operation(
            type=OPERATION_CONVERTER['funcs'][condition],
            operand=int(token)
        )

    return None


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
    rtokens = tokens[i + 1:]

    if token in KEYWORDS:
        assert len(Keyword) == 2, 'Unimplemented keywords'
        keyword = KEYWORDS[token]
        if keyword == Keyword.LET:
            if len(rtokens) == 0:
                assert False, 'EOF unexpected'
            if 'end' not in rtokens:
                assert False, '`let` statement never closed'
           
            var_name = tokens[i + 1]
            if var_name in KEYWORDS or var_name in INTRINSICS:
                assert False, 'trying to overwrite keyword/intrinsic in `let` statement'
            if var_name in vars:
                assert False, 'trying to initialize an existing variable'

            ltokens = rtokens[1:rtokens.index('end')]
            lstack: list[int] = []

            for ltoken in ltokens:
                if ltoken in vars:
                    load_variable_to_stack(lstack, vars, memory, ltoken)

                elif (operation := in_converter(ltoken)):
                    if operation.type == OperationType.PUSH_INT:
                        lstack.append(operation.operand)
                    elif operation.type == OperationType.PLUS:
                        a = lstack.pop()
                        b = lstack.pop()
                        lstack.append(a + b)
                    elif operation.type == OperationType.MULTIPLY:
                        a = lstack.pop()
                        b = lstack.pop()
                        lstack.append(a * b)
                    else:
                        assert False, f'unsupported operation {ltoken!r} in `let` statement'

                else:
                    assert False, f'unknown token {ltoken!r} in `let` statement'

            vars[var_name] = len(memory)
            lval = lstack.pop()
            memory.append(bytearray(lval.to_bytes(8, 'big')))
            ret_val += len(ltokens) + 2

            #assert False, 'LET unimplemented'
        elif keyword == Keyword.END:
            assert False, 'END unimplemented'

    elif token in INTRINSICS:
        assert False, 'TODO: intrinsics not implemented'

    elif (operation := in_converter(token)):
        # NO_OP does not need implementation
        assert len(OperationType) - 1 == 7, 'Unimplemented operation types'
        if operation.type == OperationType.PUSH_INT:
            stack.append(operation.operand)
        elif operation.type == OperationType.PLUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(a + b)
        elif operation.type == OperationType.MULTIPLY:
            a = stack.pop()
            b = stack.pop()
            stack.append(a * b)
        elif operation.type == OperationType.PRINT:
            a = stack.pop()
            print(a)
        elif operation.type == OperationType.SWAP:
            a = stack.pop()
            b = stack.pop()
            stack.append(b)
            stack.append(a)
        elif operation.type == OperationType.WRITE_MEM:
            if len(stack) < 2:
                assert False, '`@m` requires 2 elements on the stack'
            operand = stack.pop()
            ref = stack.pop()
            memory[ref] = bytearray(operand.to_bytes(8, 'big'))
            

        elif operation.type == OperationType.RET_MEM:
            assert False, 'TODO: not implemented'
        else:
            assert False, 'impossible, something wrong in `in_converter`'

    elif token in vars or (token.startswith('&') and token[1:] in vars):
        is_ref = token.startswith('&') and token[1:] in vars
        if is_ref:
            token = token[1:]
        load_variable_to_stack(stack, vars, memory, token, is_ref=is_ref)

    else:
        assert False, f'Token {token!r} not recognized'

    return ret_val

def simulate(code: str) -> None:
    stack: list[int] = []
    ptrs: dict[str, int] = {}
    memory: list[bytearray] = []
    tokens: list[str] = []

    curr_token: str = ''
    for c in code:
        if c == ' ' or c == '\n':
            if curr_token:
                tokens.append(curr_token)
                curr_token = ''
            continue
        curr_token += c
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