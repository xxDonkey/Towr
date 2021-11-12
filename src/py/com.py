import os
from globals import *
# from syscalls import SYSCALLS

# pyright: reportUnnecessaryComparison=false 

initialized: bool = False
stack_limit: int

def intiialize(_stack_limit: int) -> None:
    global initialized, stack_limit
    stack_limit = _stack_limit
    initialized = True

_UNUSED_KEYWORDS: int = 5 # import is dealt with elsewhere, params not used yet

_BUILD_WIN10: str = 'ml /c /coff /Cp %s.asm'
_LINK_WIN10: str = 'link /subsystem:console %s.obj'
_EXECUTE_WIN10: str = '%s.exe'

_DATA_ESCAPE_SEQUENCE: str = '|!DATA!|'
_VARIABLE_TYPE = 'dword'

_BYTE_SIZE: dict[str, int] = {
    'win10,x86': 64,
}

class BlockType(Enum):
    NONE    = auto()
    IF      = auto()
    ELSEIF  = auto()
    ELSE    = auto()
    WHILE   = auto()

@dataclass
class CodeBody:
    code_body: str = ''
    buffer: list[str] = field(default_factory=list)
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

    def write_buffer(self, code: str, i: int=0) -> None:
        while len(self.buffer) <= i:
            self.buffer.append('')
        self.buffer[i] += code 

    def dump_buffer(self, i: int=0) -> None:
        self.code_body += self.__get_indent() + self.buffer[i]
        self.buffer[i] = ''

def com_program(program: Program, outfile: str) -> None:
    assert initialized, '`initialize` must be called to use com.py'
    __com_program_win10_x86(program, outfile)

# asm code, new strs
_CodeRet = Tuple[str, list[bytes]]

def __com_program_win10_x86(program: Program, outfile: str, compile: bool=True, debug_output:bool=False) -> Union[str, None]:
    assert len(OperationType) == 9, 'Unhandled members of `OperationType`'
    assert len(Keyword) == 9 + _UNUSED_KEYWORDS, 'Unhandled members of `Keyword`'
    assert len(Intrinsic) == 22, 'Unhandled members of `Intrinsic`'
    
    debug_output = True
    # compile = False

    if debug_output:
        with open('out.txt', 'w') as f:
            for op in program.operations:
                f.write('%s\n' % op.__str__())

    global ifblock_c
    ifblock_c = 0

    global wblock_c
    wblock_c = 0

    global iota
    iota = 0
    
    vars: list[Variable] = []

    def generate_code_segment(operations: list[Operation], 
                              depth_map: dict[int, int],
                              block_depth: int=0,
                              existing_strs: list[bytes]=[],
                              indent:int=1
    ) -> _CodeRet:
        global ifblock_c
        global wblock_c
        global iota

        cb = CodeBody()
        cb.indent = indent
        strs: list[bytes] = existing_strs
        elseif_c: int = 0
        cblock: BlockType = BlockType.NONE
        while_cond: list[Operation] = []

        for operation in operations:
            if cblock == BlockType.WHILE:
                while_cond.append(operation)
            else:
                while_cond.clear()
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
                # TODO: fix in statements
                assert isinstance(operation.operand, str), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                cb.writecl(';; --- Push STR [%s]---;;' % operation.operand)
                encoded = operation.operand.encode('utf-8')
                size = len(encoded)
                exists = encoded in strs
                cb.writel('mov eax, %i' % size)
                cb.writel('push eax')
                cb.writel('push offset str_%i' % (len(strs) if not exists else strs.index(encoded)))
                if not exists:
                    strs.append(encoded)
            elif operation.type == OperationType.VAR_REF:
                assert isinstance(operation.operand, str), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                name, typ = operation.operand.split('/')
                cb.writecl(';; --- Push Variable to Stack [%s]---;;' % name)
                if typ == 'val':
                    cb.writel('mov eax, _%s' % name)
                    cb.writel('mov edx, [eax]')
                elif typ == 'ref':
                    cb.writel('mov edx, _%s' % name)
                else:
                    assert False, 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                cb.writel('push edx')
            elif operation.type == OperationType.PUSH_VAR_REF:
                assert isinstance(operation.operand, str), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                name, typ = operation.operand.split('/')
                cb.writecl(';; --- Push Variable Reference to Stack [%s]---;;' % name)
                if typ == 'val':
                    cb.writel('mov eax, _%s' % name)
                elif typ == 'ref':
                    cb.writel('mov eax, offset _%s' % name)
                else:
                    assert False, 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                cb.writel('push eax')
            elif operation.type == OperationType.FUNC_CALL:
                assert isinstance(operation.operand, int), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                func: Func = program.funcs[operation.operand]
                cb.writecl(';; --- Call Func [%s]---;;' % func.name)
                cb.writel('call %s' % func.name)
                cb.writel('push eax')
            elif operation.type == OperationType.RETURN:
                assert isinstance(operation.operand, int) and 0 <= operation.operand <= 1, 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                cb.writecl(';; --- Return [%s] Values From Stack ---;;' % operation.operand)
                cb.writel('ret %i' % operation.operand)
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
                assert isinstance(operation.operand, str), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                value, name = (operation.operand.split('/'))
                assert IS_INT(value), 'Error in tparser.py in `program_from_tokens`'
                value = int(value)
                cb.writecl(';; --- Allocate 1 Bytes of Data for [%s] ---;;' % name)
                cb.writel('invoke crt_malloc, 1')
                cb.writel('mov _%s, eax' % name)
                cb.writel('mov ebx, %i' % value)
                cb.writel('mov [eax], ebx')
                vars.append(Variable(name=name, value=value, malloc=False))
            elif operation.type == Keyword.LETMEM:
                assert isinstance(operation.operand, str), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
                value, name = (operation.operand.split('/'))
                assert IS_INT(value), 'Error in tparser.py in `program_from_tokens`'
                value = int(value)
                cb.writecl(';; --- Allocate %i Bytes of Data for [%s] ---;;' % (value, name))
                cb.writel('invoke crt_malloc, %i' % value)
                cb.writel('mov _%s, eax' % name)
                cb.writel('mov ebx, 0')
                cb.writel('mov [eax], ebx')
                vars.append(Variable(name=name, value=value, malloc=True))
            elif operation.type == Keyword.IF:
                cb.writecl(';; --- Check Condition for _if_%i --- ;;' % ifblock_c)
                cb.write_buffer('\n    ;; --- Jump to _if_%i if True --- ;;'% ifblock_c)
                cb.write_buffer('\n    pop eax\n')
                cb.write_buffer('    mov ebx, 1\n')
                cb.write_buffer('    cmp eax, ebx\n')
                cb.write_buffer('    je _if_%i\n' % ifblock_c)
                cblock = BlockType.IF
                depth_map[block_depth] = ifblock_c
                block_depth += 1
                ifblock_c += 1
            elif operation.type == Keyword.ELSE:
                cb.code_body = cb.code_body.replace(
                    ';; --- Otherwise Jump to _endif_%i --- ;;' % depth_map[block_depth - 1],
                    ';; --- Otherwise Jump to _else_%i --- ;;' % depth_map[block_depth - 1], 1
                )
                cb.buffer[1] = cb.buffer[1].replace('jmp _endif_%i' % depth_map[block_depth - 1], 'jmp _else_%i' % depth_map[block_depth - 1], 1)
                cb.write_buffer('\n_else_%i:\n' % ifblock_c, 1)
                block_body = ''
                if len(operation.args) > 0:
                    assert isinstance(operation.args[0], Operation), 'Error in tparser.py in `program_from_tokens`'
                    block_body, _strs = condition_body, _strs = generate_code_segment(while_cond[:-1], depth_map, 
                        block_depth=block_depth, 
                        existing_strs=existing_strs
                    )
                    strs += _strs
                cb.write_buffer(block_body, 1)
                cblock = BlockType.ELSE
            elif operation.type == Keyword.ELSEIF:
                cb.writecl(';; --- Check Condition for _elseif_%i_%i --- ;;' % (ifblock_c, elseif_c))
                cb.write_buffer('\n    ;; --- Jump to _elseif_%i_%i if True --- ;;' % (ifblock_c, elseif_c))
                cb.write_buffer('\n    pop eax\n')
                cb.write_buffer('    mov ebx, 1\n')
                cb.write_buffer('    cmp eax, ebx\n')
                cb.write_buffer('    je _elseif_%i_%i\n' % (ifblock_c, elseif_c))
                elseif_c += 1
                cblock = BlockType.ELSEIF
            elif operation.type == Keyword.WHILE:
                cb.writecl(';; --- Check Condition for _while_%i --- ;;' % wblock_c)
                # TODO: figure this out
                cb.write_buffer('\n    ;; --- Jump to _while_%i if True --- ;;' % wblock_c, 1)
                cb.write_buffer('\n    pop eax\n', 1)
                cb.write_buffer('    mov ebx, 1\n', 1)
                cb.write_buffer('    cmp eax, ebx\n', 1)
                cb.write_buffer('    je _while_%i\n' % wblock_c, 1)
                cb.write_buffer('\n    ;; --- Otherwise Jump to _endw_%i if True --- ;;' % wblock_c, 1)
                cb.write_buffer('\n    jmp _endw_%i\n' % wblock_c, 1)
                cblock = BlockType.WHILE
                depth_map[block_depth] = ifblock_c
                block_depth += 1
                wblock_c += 1
            elif operation.type == Keyword.DO:
                print('---------\n%s\n-------' % depth_map)
                cb.write_buffer('\n_while_%i:\n' % depth_map[block_depth - 1], 1)
                block_body, _strs = generate_code_segment(operation.args, depth_map, 
                    block_depth=block_depth, 
                    existing_strs=existing_strs
                )
                strs += _strs
                cb.write_buffer(block_body, 1)
                condition_body, _strs = generate_code_segment(while_cond[:-1], depth_map, 
                    block_depth=block_depth, 
                    existing_strs=existing_strs
                )
                strs += _strs
                cb.write_buffer(condition_body, 1)
                cb.write_buffer('\n    ;; --- Jump to _while_%i if True --- ;;'% depth_map[block_depth - 1], 1)
                cb.write_buffer('\n    pop eax\n', 1)
                cb.write_buffer('    mov ebx, 1\n', 1)
                cb.write_buffer('    cmp eax, ebx\n', 1)
                cb.write_buffer('    je _while_%i\n' % depth_map[block_depth - 1], 1)
            elif operation.type == Keyword.THEN:
                cb.dump_buffer()
                block_body = ''
                if len(operation.args) > 0:
                    assert isinstance(operation.args[0], Operation), 'Error in tparser.py in `program_from_tokens`'
                    block_body, _strs = generate_code_segment(operation.args, depth_map, 
                        block_depth=block_depth, 
                        existing_strs=existing_strs
                    )
                    strs += _strs
                if cblock == BlockType.IF:
                    cb.writecl(';; --- Otherwise Jump to _endif_%i --- ;;' % depth_map[block_depth - 1])
                    cb.write_buffer('jmp _endif_%i\n' % depth_map[block_depth - 1], 1)
                    cb.write_buffer('\n_if_%i: ; depth: %i\n' % (depth_map[block_depth - 1] , block_depth), 1)
                    cb.write_buffer(block_body, 1)
                elif cblock == BlockType.ELSEIF:
                    cb.write_buffer('\n_elseif_%i_%i:\n' % (depth_map[block_depth - 1], elseif_c - 1), 1)
                    cb.write_buffer(block_body, 1)
                else:
                    assert False, 'impossible'
                cb.write_buffer('\n    ;; --- Jump Out of the IF-ELSEIF-ELSE Statement --- ;;', 1)
                cb.write_buffer('\n    jmp _endif_%i\n' % depth_map[block_depth - 1], 1)
            
            elif operation.type == Keyword.END:
                cb.dump_buffer(1)
                if cblock == BlockType.WHILE:
                    cb.writel('\n_endw_%i:' % depth_map[block_depth - 1])
                elif cblock != BlockType.NONE:
                    cb.writel('\n_endif_%i:' % depth_map[block_depth - 1])
                else:
                    assert False, 'impossible'
                elseif_c = 0
                block_depth -= 1
            elif operation.type == Keyword.COUNTER:
                cb.writecl(';; --- Push INT from Internal Counter [%i] ---;;' % iota)
                cb.writel('mov eax, %i' % iota)
                cb.writel('push eax')
                iota += 1
            elif operation.type == Keyword.RESET:
                cb.writecl(';; --- Push INT from Internal Counter, Also Resets [%i] ---;;' % iota)
                cb.writel('mov eax, %i' % iota)
                cb.writel('push eax')
                iota = 0

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
            elif operation.type == Intrinsic.DIVMOD:
                cb.writecl(';; --- DIVMOD --- ;;')
                cb.writel('mov edx, 0')
                cb.writel('pop eax')
                cb.writel('pop ecx')
                cb.writel('div ecx')
                cb.writel('push eax')
                cb.writel('push edx')
            elif operation.type == Intrinsic.PRINT:
                cb.writecl(';; --- PRINT --- ;;')
                cb.writel('pop eax')
                cb.writel('printf("%i\\n", eax)')
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
                cb.writel('cmovl ecx, edx')
                cb.writel('push ecx')
            elif operation.type == Intrinsic.GREATER:
                cb.writecl(';; --- GREATER --- ;;')
                cb.writel('mov ecx, 0')
                cb.writel('mov edx, 1')
                cb.writel('pop eax')
                cb.writel('pop ebx')
                cb.writel('cmp ebx, eax')
                cb.writel('cmovg ecx, edx')
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
                cb.writel('pop eax')
                cb.writel('mov ebx, [eax]')
                cb.writel('push ebx')
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
            elif operation.type == Intrinsic.STDOUT:
                cb.writecl(';; --- Prints From Top of Stack to StdOut --- ;;')
                cb.writel('pop eax')
                cb.writel('invoke StdOut, eax')
                cb.writel('push eax')
            elif operation.type == Intrinsic.STDERR:
                assert False, 'STDERR'
            elif operation.type == Intrinsic.BYTE:
                size = _BYTE_SIZE['win10,x86']
                cb.writecl(';; --- Push Byte Size [%i] ---;;' % size)
                cb.writel('mov eax, %i' % size)
                cb.writel('push eax')
            elif operation.type == Intrinsic.AND:
                cb.writecl(';; --- AND -- ;;')
                cb.write('pop eax')
                cb.write('pop ebx')
                cb.write('and eax, ebx')
                cb.write('push eax')
            elif operation.type == Intrinsic.OR:
                cb.writecl(';; --- OR -- ;;')
                cb.write('pop eax')
                cb.write('pop ebx')
                cb.write('or eax, ebx')
                cb.write('push eax')
            elif operation.type == Intrinsic.XOR:
                cb.writecl(';; --- XOR -- ;;')
                cb.write('pop eax')
                cb.write('pop ebx')
                cb.write('xor eax, ebx')
                cb.write('push eax')
            elif operation.type == Intrinsic.NOT:
                cb.writecl(';; --- NOT -- ;;')
                cb.write('pop eax')
                cb.write('not eax')
                cb.write('push eax')
            
        return (cb.code_body, strs)
    
    cb: CodeBody = CodeBody()
    strs: list[bytes] = []
    depth_map: dict[int, int] = {}
    
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
    if len(program.funcs):
        cb.write('\n')
    for func in program.funcs:
        cb.writel('%s proc %s' % (func.name, ', '.join(f'{param}:dword' for param in func.params)))
        func_body, _strs = generate_code_segment(func.operations, depth_map, 
            block_depth=1, 
            existing_strs=strs
        )
        strs += _strs
        cb.writel(func_body)
        cb.writel('%s endp' % func.name)
    
    cb.writel('\nstart:')
    main_body, _strs = generate_code_segment(program.operations, depth_map, 
        block_depth=0, 
        existing_strs=strs
    )
    cb.writel(main_body)
    strs += _strs
    data_str: str = ''
    data_str += '\n;; --- Data Declarations --- ;;'
    data_str += '\n.data'
    data_str += '\n\n;; --- Default Program Data --- ;;'
    data_str += '\nstacksize dword 0'
    data_str += '\n\n;; --- String Literal Data --- ;;'
    for i, Str in enumerate(strs):
        data_str += '\nstr_%i db "%s", 0' % (i, Str.decode('utf-8'))
    data_str += '\n\n;; --- Uninitialized Data Declarations --- ;;'
    data_str += '\n.data?'
    data_str += '\n\n;; --- Variable Data --- ;;'
    for i, Var in enumerate(vars):
        data_str += '\n_%s %s ?' % (Var.name, _VARIABLE_TYPE)
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
        pass
        # return cb.code_body

    filepath = os.path.join(os.getcwd(), outfile)
    os.system(_BUILD_WIN10 % filepath)

    filepath = os.path.join(os.getcwd(), outfile.split('/')[-1])
    os.system(_LINK_WIN10 % filepath)
    os.system(_EXECUTE_WIN10 % filepath)