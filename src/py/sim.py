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

def sim_tokens(tokens: list[Token], vars: list[Variable], iota: int) -> Tuple[StackValue, int]:
    stack: list[StackValue] = []

    # TODO: add functions to this sim

    for token in tokens:
        if token.type == OperationType.PUSH_INT:
            stack.append(StackValue(
                datatype=DataType.INT,
                value=token.operand
            ))
        elif token.type == OperationType.PUSH_BOOL:
            stack.append(StackValue(
                datatype=DataType.BOOL,
                value=token.operand
            ))
        elif token.type == OperationType.PUSH_STR:
            assert False, 'TODO: string literals not implemented'

        elif token.type == Intrinsic.PLUS:
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

        elif token.type == Keyword.COUNTER:
            stack.append(StackValue(
                datatype=DataType.INT,
                value=iota
            ))
            iota += 1
        elif token.type == Keyword.RESET:
            stack.append(StackValue(
                datatype=DataType.INT,
                value=iota
            ))
            iota = 0

        elif token.value in (var_strs := [var.name for var in vars]):
            var = vars[var_strs.index(token.value)]
            stack.append(StackValue(
                datatype=DataType.INT,
                value=var.value
            ))

        else:
            compiler_error(token.location, f'Unrecognized token {token.value!r}', __file__)

    out = stack.pop()
    if len(stack) > 0:
        compiler_error(tokens[0].location, 'Unhandled data on stack in `LET` statement.', __file__)
    return out, iota