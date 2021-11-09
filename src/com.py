import os
from globals import *
# from syscalls import SYSCALLS

initialized: bool = False
stack_limit: int

def intiialize(_stack_limit: int) -> None:
    global initialized, stack_limit
    stack_limit = _stack_limit
    initialized = True

_UNUSED_KEYWORDS: int = 2 # import is dealt with elsewhere, params not used yet

_BUILD_WIN10: str = 'ml /c /coff /Cp %s.asm'
_LINK_WIN10: str = 'link /subsystem:console %s.obj'
_EXECUTE_WIN10: str = '%s.exe'

_DATA_ESCAPE_SEQUENCE: str = '|!DATA!|'
_VARIABLE_TYPE_CONVERSIONL: dict[DataType, str] = {
    DataType.INT: 'sdword',
    DataType.BOOL: 'byte',
    DataType.PTR: 'byte',
}
assert len(DATATYPES) == len(DataType), 'Unassigned datatypes'

class BlockType(Enum):
    IF      = auto()
    WHILE   = auto()

_BLOCK_TYPE_CONVERSION: dict[BlockType, str] = {
    BlockType.IF: 'if',
    BlockType.WHILE: 'w',
}
assert len(_BLOCK_TYPE_CONVERSION) == len(BlockType), 'Unassigned block types'

@dataclass
class CodeBody:
    code_body: str = ''
    buffer: str = ''
    indent: int = 0

    def __get_indent(self) -> str:
        assert self.indent >= 0, 'impossible, error in com.py in `__com_program_win10`'
        return ' ' * 4 * self.indent

    def write_no_indent(self, code: str) -> None:
        self.code_body += code

    def write(self, code: str) -> None:
        self.code_body += self.__get_indent() + code
    
    def writel(self, code: str) -> None:
        self.code_body += self.__get_indent() + code + '\n'

    def writecl(self, code: str) -> None:
        self.code_body += '\n' + self.__get_indent() + code + '\n'

    def write_buffer(self, code: str) -> None:
        self.buffer += code 

    def dump_buffer(self) -> None:
        self.code_body += self.__get_indent() + self.buffer
        self.buffer = ''

def com_program(program: Program, outfile: str) -> None:
    assert initialized, '`initialize` must be called to use com.py'
    __com_program_win10(program, outfile)

def __com_program_win10(program: Program, outfile: str, compile: bool=True) -> Union[str, None]:
    assert len(OperationType) == 8, 'Unhandled members of `OperationType`'
    assert len(Keyword) == 8 + _UNUSED_KEYWORDS, 'Unhandled members of `Keyword`'
    assert len(Intrinsic) == 14, 'Unhandled members of `Intrinsic`'

    def generate_main_code_body(operations: list[Operation]) -> Tuple[str, list[bytes]]:
        cb = CodeBody()
        cb.indent = 1
        blocks: list[BlockType] = []
        strs: list[bytes] = []
        for operation in operations:
            if operation.type == OperationType.PUSH_INT:
                assert isinstance(operation.operand, int), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                cb.writecl(';; --- Push INT [%i] ---;;' % operation.operand)
                cb.writel('mov eax, %i' % operation.operand)
                cb.writel('push eax')
            if operation.type == OperationType.PUSH_BOOL:
                assert isinstance(operation.operand, int) and 0 <= operation.operand <= 1, 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                cb.writecl(';; --- Push BOOL [%i] ---;;' % operation.operand)
                cb.writel('mov eax, %i' % operation.operand)
                cb.writel('push eax')
            if operation.type == OperationType.PUSH_STR:
                assert isinstance(operation.operand, str), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                cb.writecl(';; --- Push STR [%s]---;;' % operation.operand)
                encoded = operation.operand.encode('utf-8')
                size = len(encoded)
                cb.writel('mov eax, %i' % size)
                cb.writel('push eax')
                cb.writel('push offset str_%i' % len(strs))
                strs.append(encoded)
            elif operation.type == OperationType.VAR_REF:
                assert isinstance(operation.operand, str), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                cb.writecl(';; --- Push Variable to Stack [%s]---;;' % operation.operand)
                name = operation.operand
                cb.writel('mov eax, %s' % name)
                cb.writel('push eax')
            elif operation.type == OperationType.PUSH_VAR_REF:
                assert isinstance(operation.operand, str), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                cb.writecl(';; --- Push Variable Reference to Stack [%s]---;;' % operation.operand)
                name = operation.operand
                cb.writel('mov eax, offset %s' % name)
                cb.writel('push eax')
            elif operation.type == OperationType.FUNC_CALL:
                assert isinstance(operation.operand, int), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                func: Func = program.funcs[operation.operand]
                cb.writecl(';; --- Call Func [%s]---;;' % func.name)
                cb.writel('call %s' % func.name)
                cb.writel('printf("%i", did_ret)')
                cb.writel('print addr newline')
                
            elif operation.type == OperationType.WRITE_STACK_SIZE:
                cb.writecl(';; --- Write Stack Size to `stacksize` Variable ---;;')
                cb.writel('mov eax, ebp')
                cb.writel('mov ebx, esp')
                cb.writel('sub eax, ebx')
                cb.writel('mov ebx, offset stacksize')
                cb.writel('mov [ebx], eax')
            elif operation.type == OperationType.PUSH_STACK_SIZE:
                cb.writecl(';; --- Push Stack Size to Stack ---;;')
                cb.writel('mov eax, ebp')
                cb.writel('mov ebx, esp')
                cb.writel('sub eax, ebx')
                cb.writel('push eax')

            elif operation.type == Keyword.LET:
                assert False, 'LET'
            elif operation.type == Keyword.IF:
                cb.write_buffer('.if ')
                blocks.append(BlockType.IF)
            elif operation.type == Keyword.ELSE:
                cb.writecl('.else ')
            elif operation.type == Keyword.ELSEIF:
                cb.writecl('.else')
                cb.write_buffer('.endif\n\n.if ')
            elif operation.type == Keyword.WHILE:
                cb.write_buffer('.while ')
                blocks.append(BlockType.WHILE)
            elif operation.type == Keyword.DO:
                cb.writecl('pop ecx')
                cb.dump_buffer()
                cb.write_no_indent('ecx == 1\n')
            elif operation.type == Keyword.END:
                cb.writel('\n    .end%s ' % _BLOCK_TYPE_CONVERSION[blocks.pop()])

            elif operation.type == Intrinsic.PLUS:
                cb.writecl(';; --- PLUS --- ;;')
                cb.writel('pop eax')
                cb.writel('pop ebx')
                cb.writel('add eax, ebx')
                cb.writel('push eax')
            elif operation.type == Intrinsic.MINUS:
                cb.writecl(';; --- PLUS --- ;;')
                cb.writel('pop eax')
                cb.writel('pop ebx')
                cb.writel('sub eax, ebx')
                cb.writel('push eax')
            elif operation.type == Intrinsic.MULTIPLY:
                cb.writecl(';; --- MULTIPLY --- ;;')
                cb.writel('pop eax')
                cb.writel('pop ebx')
                cb.writel('mul ebx')
                cb.writel('push eax')
            elif operation.type == Intrinsic.PRINT:
                cb.writecl(';; --- PRINT --- ;;')
                cb.writel('pop eax')
                cb.writel('printf("%i", eax)')
                cb.writel('print addr newline')
            elif operation.type == Intrinsic.SWAP:
                cb.writecl(';; --- SWAP --- ;;')
                cb.writel('pop eax')
                cb.writel('pop ebx')
                cb.writel('push eax')
                cb.writel('push ebx')
            elif operation.type == Intrinsic.EQUALS:
                cb.writecl(';; --- EQUALS --- ;;')
                cb.writel('mov ecx, 0')
                cb.writel('mov edx, 1')
                cb.writel('pop eax')
                cb.writel('pop ebx')
                cb.writel('cmp eax, ebx')
                cb.writel('cmove ecx, edx')
                cb.writel('push ecx')
            elif operation.type == Intrinsic.LESS:
                cb.writecl(';; --- LESS --- ;;')
                cb.writel('mov ecx, 0')
                cb.writel('mov edx, 1')
                cb.writel('pop eax')
                cb.writel('pop ebx')
                cb.writel('cmp ebx, eax')
                cb.writel('cmovg ecx, edx')
                cb.writel('push ecx')
            elif operation.type == Intrinsic.GREATER:
                cb.writecl(';; --- GREATER --- ;;')
                cb.writel('mov ecx, 0')
                cb.writel('mov edx, 1')
                cb.writel('pop eax')
                cb.writel('pop ebx')
                cb.writel('cmp ebx, eax')
                cb.writel('cmovl ecx, edx')
                cb.writel('push ecx')
            elif operation.type == Intrinsic.DUP:
                cb.writecl(';; --- DUP --- ;;')
                cb.writel('pop eax')
                cb.writel('push eax')
                cb.writel('push eax')
            elif operation.type == Intrinsic.DROP:
                cb.writecl(';; --- DROP --- ;;')
                cb.writel('pop eax')
            elif operation.type == Intrinsic.STORE: 
                cb.writecl(';; --- STORE --- ;;')
                cb.writel('pop eax')
                cb.writel('pop ebx')
                cb.writel('mov [ebx], eax')
            elif operation.type == Intrinsic.READ: 
                cb.writecl(';; --- READ --- ;;')
                
            elif operation.type == Intrinsic.INC:
                cb.writecl(';; --- INCREMENT --- ;;')
                cb.writel('pop eax')
                cb.writel('inc eax')
                cb.writel('push eax')
            elif operation.type == Intrinsic.DEC:
                cb.writecl(';; --- DECREMENT --- ;;')
                cb.writel('pop eax')
                cb.writel('dec eax')
                cb.writel('push eax')

        return (cb.code_body, strs)

    def generate_variable_declarations(vars: list[Variable]) -> str:
        data_str: str = ''
        for var in vars:
            data_str += '\n;; --- Create [%s] With Value %s ---;;' % (var.name, str(var.value))
            data_str += '\n%s %s %i' % (var.name, _VARIABLE_TYPE_CONVERSIONL[var.datatype], var.value) 
        return data_str

    # for o in program.operations: print(f'-- {o} --')
    
    cb: CodeBody = CodeBody()
    strs: list[bytes] = []
    
    cb.writel(';; Necessary initialization statements ;;')
    cb.writel('.686')
    cb.writel('.model flat, stdcall')
    cb.writel('assume fs:nothing\n')

    cb.writel(';; Necessary include statments ;;')
    cb.writel('include /masm32/macros/macros.asm')
    cb.writel('include /masm32/include/kernel32.inc')
    cb.writel('include /masm32/include/msvcrt.inc')
    cb.writel('include /masm32/include/masm32.inc')
    cb.writel('includelib /masm32/lib/kernel32')
    cb.writel('includelib /masm32/lib/msvcrt')
    cb.writel('includelib /masm32/lib/masm32')

    cb.writel(_DATA_ESCAPE_SEQUENCE)

    cb.writel('\n;; --- Code Body ---;;')
    cb.writel('.code')

    # TODO: returns
    func_data: str = ''
    if len(program.funcs):
        cb.write('\n')
    for func in program.funcs:
        cb.writel('%s proc %s' % (func.name, ', '.join(f'{param}:dword' for param in func.params)))
        func_body, _strs = generate_main_code_body(func.operations)
        strs += _strs
        cb.writel(func_body)
        func_data += '\n%s' % generate_variable_declarations(func.vars)
        cb.writel('    ret 0')
        cb.writel('%s endp' % func.name)
    
    cb.writel('\nstart:')
    main_body, _strs = generate_main_code_body(program.operations)
    cb.writel(main_body)
    strs += _strs
            
    data_str: str = ''
    data_str += '\n;; --- Data Declarations --- ;;'
    data_str += '\n.data'
    data_str += '\n\n;; --- Default Program Data --- ;;'
    data_str += '\ndid_ret byte 0'
    data_str += '\nret_val dword 0'
    data_str += '\nstacksize dword 0'
    data_str += '\nnewline db " ", 10, 0'
    data_str += '\n\n;; --- Variable Data --- ;;'
    data_str += generate_variable_declarations(program.vars)
    data_str += func_data
    data_str += '\n\n;; --- String Literal Data --- ;;'
    for i, Str in enumerate(strs):
        data_str += '\nstr_%i db "%s"' % (i, Str.decode('utf-8'))
    cb.code_body = cb.code_body.replace(_DATA_ESCAPE_SEQUENCE, data_str)

    cb.indent = 0
    cb.writel(';; Ends the program ;;')
    cb.writel('invoke ExitProcess, 0')
    cb.writel('end start')
    cb.writel('end')

    if compile:
        with open(os.path.join(os.getcwd(), f'{outfile}.asm'), 'w') as out:
            out.write(cb.code_body)
    else:
        return cb.code_body

    filepath = os.path.join(os.getcwd(), outfile)
    os.system(_BUILD_WIN10 % filepath)

    filepath = os.path.join(os.getcwd(), outfile.split('/')[-1])
    os.system(_LINK_WIN10 % filepath)
    os.system(_EXECUTE_WIN10 % filepath)
