import os
from globals import *

initialized: bool = False
stack_limit: int

def intiialize(_stack_limit: int) -> None:
    global initialized, stack_limit
    stack_limit = _stack_limit
    initialized = True

_BUILD_WIN10: str = 'ml /c /coff /Cp %s.asm'
_LINK_WIN10: str = 'link /subsystem:console %s.obj'
_EXECUTE_WIN10: str = '%s.exe'

@dataclass
class CodeBody:
    code_body: str = ''
    buffer: str = ''

    def write(self, code: str) -> None:
        self.code_body += code
    
    def writel(self, code: str) -> None:
        self.code_body += code + '\n'

    def writecl(self, code: str) -> None:
        self.code_body += '\n' + code + '\n'

    def write_buffer(self, code: str) -> None:
        self.buffer += code 

    def dump_buffer(self) -> None:
        self.code_body += self.buffer
        self.buffer = ''

def com_program(program: Program, outfile: str) -> None:
    assert initialized, '`initialize` must be called to use com.py'
    __com_program_win10(program, outfile)

def __com_program_win10(program: Program, outfile: str) -> None:
    # for o in program.operations: print(f'-- {o} --')
    cb: CodeBody = CodeBody()

    cb.writel(';; Necessary initialization statements ;;')
    cb.writel('.686')
    cb.writel('.model flat, stdcall\n')

    cb.writel(';; Necessary include statments ;;')
    cb.writel('include /masm32/macros/macros.asm')
    cb.writel('include /masm32/include/kernel32.inc')
    cb.writel('include /masm32/include/msvcrt.inc')
    cb.writel('include /masm32/include/masm32.inc')
    cb.writel('includelib /masm32/lib/kernel32')
    cb.writel('includelib /masm32/lib/msvcrt')
    cb.writel('includelib /masm32/lib/\n')

    cb.writel(';; Code body ;;')
    cb.writel('.code')
    
    cb.writel('start:')
    for operation in program.operations:
        assert len(OperationType) == 5, 'Unhandled members of `OperationType`'
        assert len(Keyword) == 9, 'Unhandled members of `Keyword`'
        assert len(Intrinsic) == 7, 'Unhandled members of `Intrinsic`'

        if operation.type == OperationType.PUSH_INT:
            assert isinstance(operation.operand, int), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
            cb.writecl(';; --- Push INT %i ---;;' % operation.operand)
            cb.writel('mov eax, %i' % operation.operand)
            cb.writel('push eax')
        if operation.type == OperationType.PUSH_BOOL:
            assert isinstance(operation.operand, int) and 0 <= operation.operand <= 1, 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
            cb.writecl(';; --- Push BOOL %i ---;;' % operation.operand)
            cb.writel('mov eax, %i' % operation.operand)
            cb.writel('push eax')
            assert False, 'PUSH_BOOL'
        if operation.type == OperationType.PUSH_STR:
            assert isinstance(operation.operand, str), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
            assert False, 'PUSH_STR'
        elif operation.type == OperationType.PUSH_STACK_SIZE:
            assert False, 'PUSH_STACK_SIZE'
        elif operation.type == OperationType.CHECK_STACK_SIZE_G:
            assert False, 'CHECK_STACK_SIZE_G'

        elif operation.type == Keyword.LET:
            assert False, 'LET'
        elif operation.type == Keyword.IF:
            cb.write_buffer('.if ')
        elif operation.type == Keyword.ELSE:
            cb.writel('\n.else ')
        elif operation.type == Keyword.ELSEIF:
            cb.writel('\n.else')
            cb.write_buffer('.endif\n\n.if ')
        elif operation.type == Keyword.DO:
            cb.writecl('pop ecx')
            cb.dump_buffer()
            cb.write('ecx == 1\n')
        elif operation.type == Keyword.END:
            cb.writel('\n.endif ')

        elif operation.type == Intrinsic.PLUS:
            cb.writecl(';; --- PLUS --- ;;')
            cb.writel('pop eax')
            cb.writel('pop ebx')
            cb.writel('add eax, ebx')
            cb.writel('push eax')
        elif operation.type == Intrinsic.MULTIPLY:
            cb.writecl(';; --- MULTIPLY --- ;;')
            cb.writel('pop eax')
            cb.writel('pop ebx')
            cb.writel('mul eax, ebx')
            cb.writel('push eax')
        elif operation.type == Intrinsic.PRINT:
            cb.writecl(';; --- PRINT --- ;;')
            cb.writel('pop ecx')
            cb.writel('printf("%i", ecx)')
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
            



    cb.writel('\n;; Ends the program ;;')
    cb.writel('end start')

    with open(os.path.join(os.getcwd(), f'{outfile}.asm'), 'w') as out:
        out.write(cb.code_body)

    filepath = os.path.join(os.getcwd(), outfile)
    os.system(_BUILD_WIN10 % filepath)

    filepath = os.path.join(os.getcwd(), outfile.split('/')[-1])
    os.system(_LINK_WIN10 % filepath)
    os.system(_EXECUTE_WIN10 % filepath)
