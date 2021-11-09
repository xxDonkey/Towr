import os
from globals import *
from sim import sim_tokens
from tokenizer import tokenize_src

_OPERATION_TYPE_NO_STATEMENTS: int = 3

def rindex(tokens: list[str], value: str) -> int:
    for index, item in enumerate(reversed(tokens)):
        if item == value:
            return len(tokens) - index - 1
    return -1

def program_from_tokens(tokens: list[Token]) -> Program:
    operations: list[Operation] = []
    vars: list[Variable]        = []
    funcs: list[Func]           = []
    
    stack_size: int = 0
    tp: int = 0
    while tp < len(tokens):
        ctoken = tokens[tp]
        rtokens: list[Token] = tokens[tp + 1:]
        rtoken_strs: list[str] = [token.value for token in rtokens]
        adv: int = 1

        assert len(OperationType) == 3 + _OPERATION_TYPE_NO_STATEMENTS, 'Unhandled members of `OperationType`'
        assert len(Keyword) == 9, 'Unhandled members of `Keyword`'
        assert len(Intrinsic) == 10, 'Unhandled members of `Intrinsic`'

        if (ctoken.type == OperationType.PUSH_INT or
            ctoken.type == OperationType.PUSH_BOOL):
            operations.append(Operation(
                type=OperationType(ctoken.type),
                operand=ctoken.operand
            ))
            stack_size += 1
        elif ctoken.type == OperationType.PUSH_STR:
            operations.append(Operation(
                type=OperationType.PUSH_STR,
                operand=ctoken.str_operand
            ))
            stack_size += 2
        elif (ctoken.type == Intrinsic.PLUS     or
              ctoken.type == Intrinsic.MINUS    or
              ctoken.type == Intrinsic.MULTIPLY or
              ctoken.type == Intrinsic.PRINT    or
              ctoken.type == Intrinsic.EQUALS   or 
              ctoken.type == Intrinsic.GREATER  or
              ctoken.type == Intrinsic.LESS     or
              ctoken.type == Intrinsic.DUP      or
              ctoken.type == Intrinsic.DROP): 
            operations.append(Operation(
                type=ctoken.type,
                operand=0
            ))
            stack_size -= 1
        elif ctoken.type == Intrinsic.SWAP: # 0
            operations.append(Operation(
                type=ctoken.type,
                operand=0
            ))

        elif ctoken.type == Keyword.LET:
            end_str: str = KEYWORDS_INV[Keyword.END]
            if end_str not in rtoken_strs:
                compiler_error(ctoken.location, '`LET` statement never closed')
            eidx = rtoken_strs.index(end_str)
            rtokens = rtokens[:eidx]
            ntoken = rtokens.pop(0)
            CHECK_ASSIGNMENT(ntoken)
            value = sim_tokens(rtokens, vars)
            vars.append(Variable(**value.__dict__, name=ntoken.value))
            adv = len(rtokens) + 3 # rtokens does not include var name or end keyword, we want to skip end
        elif ctoken.type == Keyword.FUNC:
            assert False, 'TODO: `FUNC` not implemented'
        elif ctoken.type == Keyword.IF:
            do_str: str = KEYWORDS_INV[Keyword.DO]
            if do_str not in rtoken_strs:
                compiler_error(ctoken.location, '`IF` statement expects `DO` statement')
            operations.append(Operation(
                type=Keyword.IF,
                operand=0
            ))
        elif ctoken.type == Keyword.ELSE:
            operations.append(Operation(
                type=Keyword.ELSE,
                operand=0
            ))
        elif ctoken.type == Keyword.ELSEIF:
            do_str: str = KEYWORDS_INV[Keyword.DO]
            if do_str not in rtoken_strs:
                compiler_error(ctoken.location, '`ELSEIF` statement expects `DO` statement')
            operations.append(Operation(
                type=Keyword.ELSEIF,
                operand=0
            ))
        elif ctoken.type == Keyword.WHILE:
            do_str: str = KEYWORDS_INV[Keyword.DO]
            if do_str not in rtoken_strs:
                compiler_error(ctoken.location, '`WHILE` statement expects `DO` statement')
            operations.append(Operation(
                type=Keyword.WHILE,
                operand=0
            ))
        elif ctoken.type == Keyword.DO:
            end_str: str = KEYWORDS_INV[Keyword.END]
            else_str: str = KEYWORDS_INV[Keyword.ELSE]
            elseif_str: str = KEYWORDS_INV[Keyword.ELSEIF]
            if end_str not in rtoken_strs and else_str not in rtoken_strs and elseif_str not in rtoken_strs:
                compiler_error(ctoken.location, '`IF` statement never closed')
            operations.append(Operation(
                type=Keyword.DO,
                operand=0
            ))
        elif ctoken.type == Keyword.IMPORT:
            ntoken = rtokens.pop(0)
            if not IS_STR(ntoken.value):
                compiler_error(ntoken.location, '`IMPORT` statement expects a proceeding string literal')
            import_val = ntoken.value[1:-1]
            if not import_val.endswith('.towr'):
                compiler_error(ntoken.location, '`IMPORT` statement expects a Towr file')
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
        elif ctoken.type == Keyword.END:
            operations.append(Operation(
                type=Keyword.END,
                operand=0
            ))
        elif ctoken.value in (var_strs := [var.name for var in vars]):
            var: Variable = vars[var_strs.index(ctoken.value)]
            operations.append(Operation(
                type=OperationType.VAR_REF,
                 operand=var.name
            ))

        else:
            compiler_error(ctoken.location, f'Unrecognized token {ctoken.value!r}')

        tp += adv 



    program: Program = Program(operations=operations, 
                               vars      =vars, 
                               funcs     =funcs, 
                               tokens    =tokens)
    return program