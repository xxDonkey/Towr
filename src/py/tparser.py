import os
from globals import *
from sim import sim_tokens
from tokenizer import tokenize_src

_OPERATION_TYPE_NO_STATEMENTS: int = 6

def rindex(tokens: list[str], value: str) -> int:
    for index, item in enumerate(reversed(tokens)):
        if item == value:
            return len(tokens) - index - 1
    return -1

def is_closed(closing: list[Keyword], tokens: list[Token]) -> Tuple[bool, int]:
    is_closed = False
    depth = 0
    idx = 0
    for i, token in enumerate(tokens):
        match token.type:
            case Keyword.IF | Keyword.WHILE:
                depth += 1
            case kw if kw in closing:
                depth -= 1
        if depth < 0:
            is_closed = True
            idx = i
            break
    return (is_closed, idx)

def program_from_tokens(tokens: list[Token], start_vars: list[Variable]=[]) -> Program:
    operations: list[Operation] = []
    vars: list[Variable]        = start_vars
    funcs: list[Func]           = []
    iota: int = 0
    tp: int = 0
    while tp < len(tokens):
        ctoken = tokens[tp]
        rtokens: list[Token] = tokens[tp + 1:]
        rtoken_strs: list[str] = [token.value for token in rtokens]
        adv: int = 1
    
        assert len(OperationType) == 3 + _OPERATION_TYPE_NO_STATEMENTS, 'Unhandled members of `OperationType`'
        assert len(Keyword) == 14, 'Unhandled members of `Keyword`'
        assert len(Intrinsic) == 22, 'Unhandled members of `Intrinsic`'

        match ctoken:
            # OperationType Handler
            case Token(OperationType.PUSH_STR, _, Str, _, _):
                operations.append(Operation(
                    type=OperationType.PUSH_STR,
                    operand=Str
                ))
            case Token(_type, operand, _, _, _) if isinstance(_type, OperationType):
                operations.append(Operation(
                    type=_type,
                    operand=operand
                ))

            # Intrinsic Handler
            case Token(_type, _, _, _, _) if isinstance(_type, Intrinsic):
                operations.append(Operation(
                    type=_type,
                    operand=0
                ))

            # Keyword Handler
            case Token(Keyword.LET | Keyword.LETMEM, _, _, loc, _):
                end = KEYWORDS_INV[Keyword.END]
                closed, _ = is_closed([Keyword.END], rtokens)
                if not closed:
                    compiler_error(loc, '', __file__)
                end_index = rtoken_strs.index(end)
                rtokens = rtokens[:end_index]
                ntoken = rtokens.pop(0)
                CHECK_ASSIGNMENT(ntoken)
                value, new_iota = sim_tokens(rtokens, vars, iota)
                iota = new_iota
                vars.append(Variable(name=ntoken.value, value=value.value, malloc=(ctoken.type == Keyword.LETMEM)))
                operations.append(Operation(
                    type=Keyword(ctoken.type),
                    operand='%i/%s' % (value.value, ntoken.value)
                ))            
                adv = len(rtokens) + 3
            case Token(Keyword.COUNTER | Keyword.RESET, _, _, _, _):
                operations.append(Operation(
                    type=Keyword(ctoken.type),
                    operand=iota
                ))
                iota += 1 if (ctoken.type == Keyword.COUNTER) else -iota
            case Token(Keyword.IF, _, _, loc, _):
                closed, _ = is_closed([Keyword.THEN], rtokens)
                if not closed:
                    compiler_error(loc, '`IF` statement expects `THEN` statement', __file__)
                operations.append(Operation(
                    type=Keyword.IF,
                    operand=0
                ))
            case Token(Keyword.ELSEIF, _, _, loc, _):
                closed, _ = is_closed([Keyword.THEN], rtokens)
                if not closed:
                    compiler_error(loc, '`IF` statement expects `THEN` statement', __file__)
                operations.append(Operation(
                    type=Keyword.ELSEIF,
                    operand=0
                ))
            case Token(Keyword.ELSE, _, _, loc, _):
                closed, idx = is_closed([Keyword.END], rtokens)
                if not closed:
                    compiler_error(loc, '`ELSE` statement never closed', __file__)
                rtokens = rtokens[:idx]
                program = program_from_tokens(rtokens)
                operations.append(Operation(
                    type=Keyword.ELSE,
                    operand=0,
                    args=program.operations
                ))
                adv = len(rtokens) + 1
            case Token(Keyword.THEN, _, _, loc, _):
                closed, idx = is_closed([Keyword.ELSEIF, Keyword.ELSE, Keyword.END], rtokens)
                if not closed:
                    compiler_error(loc, '`IF` statement never closed', __file__)
                rtokens = rtokens[:idx]
                program = program_from_tokens(rtokens)
                operations.append(Operation(
                    type=Keyword.THEN,
                    operand=0,
                    args=program.operations
                ))
                adv = len(rtokens) + 1
            case Token(Keyword.WHILE, _, _, loc, _):
                closed, _ = is_closed([Keyword.DO], rtokens)
                if not closed:
                    compiler_error(loc, '`WHILE` statement expects `DO` statement', __file__)
                operations.append(Operation(
                    type=Keyword.WHILE,
                    operand=0
                ))
            case Token(Keyword.DO, _, _, loc, _):
                closed, idx = is_closed([Keyword.END], rtokens)
                if not closed:
                    compiler_error(loc, '`WHILE` statement never closed', __file__)
                rtokens = rtokens[:idx]
                program = program_from_tokens(rtokens)
                operations.append(Operation(
                    type=Keyword.DO,
                    operand=0,
                    args=program.operations
                ))
                adv = len(rtokens) + 1
            case Token(Keyword.END, _, _, _, _):
                operations.append(Operation(
                    type=Keyword.END,
                    operand=0
                ))
            case Token(Keyword.IMPORT, _, _, loc, _):
                ntoken = rtokens.pop(0)
                if not IS_STR(ntoken.value):
                    compiler_error(loc, '`IMPORT` statement expects a proceeding string literal', __file__)
                import_val = ntoken.value[1:-1]
                if not import_val.endswith('.towr'):
                    compiler_error(loc, '`IMPORT` statement expects a .Towr file', __file__)
                import_path = os.path.join(os.getcwd(), import_val)
                code_body: str
                with open(import_path, 'r') as file:
                    code_body = file.read()
                imported_tokens = tokenize_src(TowrFile(
                    code_body=code_body,
                    filename=import_path
                ))
                program = program_from_tokens(imported_tokens)
                operations += program.operations
                vars += program.vars
                funcs += program.funcs
                adv = 2
            case Token(Keyword.FUNC, _, _, _, _):
                assert False,'FUNC'
            case Token(Keyword.PARAMS, _, _, _, _):
                assert False,'PARAMS'

            # Variables
            case Token(None, _, _, _, value) if value in (var_strs := [var.name for var in vars]):
                var: Variable = vars[var_strs.index(ctoken.value)]
                _type = 'ref' if var.malloc else 'val'
                operations.append(Operation(
                    type=OperationType.VAR_REF,
                    operand='%s/%s' % (var.name, _type)
                ))

            # Variable References
            case Token(None, _, _, _, value) if value.startswith('&') and (val := ctoken.value[1:]) in (var_strs := [var.name for var in vars]):
                var: Variable = vars[var_strs.index(val)]
                _type = 'ref' if var.malloc else 'val'
                operations.append(Operation(
                    type=OperationType.PUSH_VAR_REF,
                    operand='%s/%s' % (var.name, _type)
                ))

            # Function Call
            case Token(None, _, _, _, value) if value in (funcs_strs := [func.name for func in funcs]):
                idx = funcs_strs.index(ctoken.value)
                operations.append(Operation(
                    type=OperationType.FUNC_CALL,
                    operand=idx
                ))

            case _:
               compiler_error(ctoken.location, f'Unrecognized token {ctoken.value!r}', __file__)

        tp += adv 



    program: Program = Program(operations=operations, 
                               vars      =vars, 
                               funcs     =funcs, 
                               tokens    =tokens)
    return program