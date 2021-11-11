from globals import *

ARTHIMETIC_TYPE_CONVESTIONS: dict[Tuple[DataType, DataType], DataType] = {
    (DataType.INT,  DataType.INT)  : DataType.INT,
    (DataType.INT,  DataType.BOOL) : DataType.INT,
    (DataType.BOOL, DataType.INT)  : DataType.INT,
    (DataType.BOOL, DataType.BOOL) : DataType.BOOL, #(overflow on addition)
    (DataType.INT,  DataType.PTR)  : DataType.PTR,
    (DataType.PTR,  DataType.INT)  : DataType.PTR,
    (DataType.PTR,  DataType.PTR)  : DataType.PTR,
    (DataType.PTR,  DataType.BOOL) : DataType.PTR,
    (DataType.BOOL, DataType.PTR)  : DataType.PTR,
}

def sim_tokens(tokens: list[Token], vars: list[Variable], check_stack_size: bool=False) -> StackValue:
    stack: list[StackValue] = []
    stack_size: int = 0

    # TODO: add functions to this sim

    for token in tokens:
        if token.type == OperationType.PUSH_INT:
            if check_stack_size:
                stack_size += 1
                continue
            stack.append(StackValue(
                datatype=DataType.INT,
                value=token.operand
            ))
        elif token.type == OperationType.PUSH_BOOL:
            if check_stack_size:
                stack_size += 1
                continue
            stack.append(StackValue(
                datatype=DataType.BOOL,
                value=token.operand
            ))
        elif token.type == OperationType.PUSH_STR:
            if check_stack_size:
                stack_size += 2
                continue
            assert False, 'TODO: string literals not implemented'

        elif token.type == Intrinsic.PLUS:
            if check_stack_size:
                stack_size -= 1
                continue
            a = stack.pop()
            b = stack.pop()
            dt_key = (a.datatype, b.datatype)
            if dt_key not in ARTHIMETIC_TYPE_CONVESTIONS:
                assert False, 'Unhandled datatype arithmetic'
            dt = ARTHIMETIC_TYPE_CONVESTIONS[dt_key]
            value = a.value + b.value
            if dt == DataType.BOOL:
                value %= 2
            stack.append(StackValue(
                datatype=dt,
                value=value
            ))
        elif token.type == Intrinsic.MULTIPLY:
            if check_stack_size:
                stack_size -= 1
                continue
            a = stack.pop()
            b = stack.pop()
            dt_key = (a.datatype, b.datatype)
            if dt_key not in ARTHIMETIC_TYPE_CONVESTIONS:
                assert False, 'Unhandled datatype arithmetic'
            dt = ARTHIMETIC_TYPE_CONVESTIONS[dt_key]
            value = a.value * b.value
            stack.append(StackValue(
                datatype=dt,
                value=value
            ))

        elif token.value in (var_strs := [var.name for var in vars]):
            if check_stack_size:
                stack_size += 1
                continue
            var = vars[var_strs.index(token.value)]
            stack.append(StackValue(
                datatype=DataType.INT,
                value=var.value
            ))
        
        elif check_stack_size:
            """ Things that only need to check the stack size of. """
            if token.type == Intrinsic.EQUALS or token.type == Intrinsic.GREATER or token.type == Intrinsic.LESS:
                stack_size -= 1

        else:
            compiler_error(token.location, f'Unrecognized token {token.value!r}', __file__)

       

    if check_stack_size:
        return StackValue(
            datatype=DataType.INT,
            value=stack_size
        )

    out = stack.pop()
    if len(stack) > 0:
        compiler_error(tokens[0].location, 'Unhandled data on stack in `LET` statement.', __file__)
    return out