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
        assert len(Keyword) == 13, 'Unhandled members of `Keyword`'
        assert len(Intrinsic) == 22, 'Unhandled members of `Intrinsic`'

        if (ctoken.type == OperationType.PUSH_INT or
            ctoken.type == OperationType.PUSH_BOOL):
            operations.append(Operation(
                type=OperationType(ctoken.type),
                operand=ctoken.operand
            ))
        elif ctoken.type == OperationType.PUSH_STR:
            operations.append(Operation(
                type=OperationType.PUSH_STR,
                operand=ctoken.str_operand
            ))
        elif ctoken.type == Intrinsic.SWAP: # 0
            operations.append(Operation(
                type=ctoken.type,
                operand=0
            ))
        elif isinstance(ctoken.type, Intrinsic): 
            operations.append(Operation(
                type=ctoken.type,
                operand=0
            ))

        elif ctoken.type == Keyword.LET:
            end_str: str = KEYWORDS_INV[Keyword.END]
            if end_str not in rtoken_strs:
                compiler_error(ctoken.location, '`LET` statement never closed', __file__)
            eidx = rtoken_strs.index(end_str)
            rtokens = rtokens[:eidx]
            ntoken = rtokens.pop(0)
            CHECK_ASSIGNMENT(ntoken)
            value, new_iota = sim_tokens(rtokens, vars, iota)
            iota = new_iota
            vars.append(Variable(name=ntoken.value, value=value.value))
            operations.append(Operation(
                type=Keyword.LET,
                operand='%i/%s' % (value.value, ntoken.value)
            ))            
            adv = len(rtokens) + 3 # rtokens does not include var name or end keyword, we want to skip end
        elif ctoken.type == Keyword.LETMEM:
            end_str: str = KEYWORDS_INV[Keyword.END]
            if end_str not in rtoken_strs:
                compiler_error(ctoken.location, '`LET` statement never closed', __file__)
            eidx = rtoken_strs.index(end_str)
            rtokens = rtokens[:eidx]
            ntoken = rtokens.pop(0)
            CHECK_ASSIGNMENT(ntoken)
            value, new_iota = sim_tokens(rtokens, vars, iota)
            iota = new_iota
            vars.append(Variable(name=ntoken.value, value=value.value, malloc=True))
            operations.append(Operation(
                type=Keyword.LETMEM,
                operand='%i/%s' % (value.value, ntoken.value)
            )) 
            adv = len(rtokens) + 3 # rtokens does not include var name or end keyword, we want to skip end
        elif ctoken.type == Keyword.FUNC:
            params_str: str = KEYWORDS_INV[Keyword.PARAMS]
            if params_str not in rtoken_strs:
                compiler_error(ctoken.location, '`FUNC` statement expects params', __file__)
            pidx = rtoken_strs.index(params_str)
            rtokens = rtokens[:pidx]
            ntoken = rtokens.pop(0)
            CHECK_ASSIGNMENT(ntoken)
            params = [token.value for token in rtokens]
            funcs.append(Func(
                name=ntoken.value,
                params=params,
                operations=[],
                vars=[],
                location=ctoken.location
            ))
            adv = len(rtokens) + 2
        elif ctoken.type == Keyword.IF:
            do_str: str = KEYWORDS_INV[Keyword.DO]
            if do_str not in rtoken_strs:
                compiler_error(ctoken.location, '`IF` statement expects `DO` statement', __file__)
            operations.append(Operation(
                type=Keyword.IF,
                operand=0
            ))
        elif ctoken.type == Keyword.ELSE:
            end_str: str = KEYWORDS_INV[Keyword.END]
            if not end_str in rtoken_strs:
                compiler_error(ctoken.location, '`ELSE` statement never closed', __file__)
            eidx = rtoken_strs.index(end_str)
            rtokens = rtokens[:eidx]
            program = program_from_tokens(rtokens)
            operations.append(Operation(
                type=Keyword.ELSE,
                operand=0,
                args=program.operations
            ))
            adv = len(rtokens) + 1
        elif ctoken.type == Keyword.ELSEIF:
            do_str: str = KEYWORDS_INV[Keyword.DO]
            if do_str not in rtoken_strs:
                compiler_error(ctoken.location, '`ELSEIF` statement expects `DO` statement', __file__)
            operations.append(Operation(
                type=Keyword.ELSEIF,
                operand=0
            ))
        elif ctoken.type == Keyword.WHILE:
            do_str: str = KEYWORDS_INV[Keyword.DO]
            if do_str not in rtoken_strs:
                compiler_error(ctoken.location, '`WHILE` statement expects `DO` statement', __file__)
            operations.append(Operation(
                type=Keyword.WHILE,
                operand=0
            ))
        elif ctoken.type == Keyword.DO:
            end_str: str = KEYWORDS_INV[Keyword.END]
            else_str: str = KEYWORDS_INV[Keyword.ELSE]
            elseif_str: str = KEYWORDS_INV[Keyword.ELSEIF]
            if not end_str in rtoken_strs and not else_str in rtoken_strs and not elseif_str in rtoken_strs:
                compiler_error(ctoken.location, '`IF` statement never closed', __file__)
            depth: int = 0
            i: int = 0
            for i, token in enumerate(rtokens):
                if token.type == Keyword.LET or token.type == Keyword.IF or token.type == Keyword.WHILE:
                    depth += 1
                elif token.type == Keyword.END or token.type == Keyword.ELSEIF or token.type == Keyword.ELSE:
                    depth -= 1
                if depth < 0:
                    break
            rtokens = rtokens[:i]
            program = program_from_tokens(rtokens)
            operations.append(Operation(
                type=Keyword.DO,
                operand=0,
                args=program.operations
            ))
            adv = len(rtokens) + 1
        elif ctoken.type == Keyword.IMPORT:
            ntoken = rtokens.pop(0)
            if not IS_STR(ntoken.value):
                compiler_error(ntoken.location, '`IMPORT` statement expects a proceeding string literal', __file__)
            import_val = ntoken.value[1:-1]
            if not import_val.endswith('.towr'):
                compiler_error(ntoken.location, '`IMPORT` statement expects a Towr file', __file__)
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
        elif ctoken.type == Keyword.PARAMS:
            end_str: str = KEYWORDS_INV[Keyword.END]
            if end_str not in rtoken_strs:
                compiler_error(ctoken.location, '`FUNC` statement never closed', __file__)
            depth: int = 0
            i: int = 0
            for i, token in enumerate(rtokens):
                if token.type == Keyword.LET or token.type == Keyword.IF or token.type == Keyword.WHILE:
                    depth += 1
                elif token.type == Keyword.END:
                    depth -= 1
                if depth < 0:
                    break
            btokens: list[Token] = rtokens[:i]
            fprogram = program_from_tokens(btokens)
            funcs[-1].operations = fprogram.operations + [
                # Addition end of function operations
                Operation(Keyword.IF, operand=0),
                Operation(OperationType.PUSH_STACK_SIZE, operand=0),
                Operation(OperationType.PUSH_INT, operand=4),
                Operation(Intrinsic.EQUALS, operand=0),
                Operation(Keyword.DO, operand=0),
                # There is a value on the stack, save it to eax (by droping)
                Operation(Intrinsic.DROP, operand=0),
                Operation(Keyword.END, operand=0),
                Operation(OperationType.RETURN, operand=0),
            ]
            funcs[-1].vars = fprogram.vars
            adv = len(btokens) + 2
        elif ctoken.type == Keyword.COUNTER:
            operations.append(Operation(
                type=Keyword.COUNTER,
                operand=0
            ))
            iota += 1
        elif ctoken.type == Keyword.RESET:
            operations.append(Operation(
                type=Keyword.RESET,
                operand=0
            ))
            iota = 0
        # variable
        elif ctoken.value in (var_strs := [var.name for var in vars]):
            var: Variable = vars[var_strs.index(ctoken.value)]
            typ = 'val'
            if var.malloc:
                typ = 'ref'
            operations.append(Operation(
                type=OperationType.VAR_REF,
                operand='%s/%s' % (var.name, typ)
            ))
        # variable reference
        elif ctoken.value.startswith('&') and (val := ctoken.value[1:]) in (var_strs := [var.name for var in vars]):
            var: Variable = vars[var_strs.index(val)]
            typ = 'val'
            if var.malloc:
                print('MALLOC: %s' % var.name)
                typ = 'ref'
            operations.append(Operation(
                type=OperationType.PUSH_VAR_REF,
                operand='%s/%s' % (var.name, typ)
            ))
        # function
        elif ctoken.value in (funcs_strs := [func.name for func in funcs]):
            idx = funcs_strs.index(ctoken.value)
            operations.append(Operation(
                type=OperationType.FUNC_CALL,
                operand=idx
            ))

        else:
            compiler_error(ctoken.location, f'Unrecognized token {ctoken.value!r}', __file__)

        tp += adv 



    program: Program = Program(operations=operations, 
                               vars      =vars, 
                               funcs     =funcs, 
                               tokens    =tokens)
    return program