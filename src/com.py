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
    indent: int = 0

    def __get_indent(self) -> str:
        assert self.indent >= 0, 'impossible, error in com.py in `__com_program_win10`'
        return ' ' * 2 * self.indent

    def write(self, code: str) -> None:
        self.code_body += self.__get_indent() + code
    
    def writel(self, code: str) -> None:
        self.code_body += self.__get_indent() + code + '\n'

def com_program(program: Program, outfile: str) -> None:
    assert initialized, '`initialize` must be called to use com.py'
    __com_program_win10(program, outfile)

def __com_program_win10(program: Program, outfile: str) -> None:
    cb: CodeBody = CodeBody()
    indentation: int = 0

    cb.writel(';; Necessary initialization statements ;;')
    cb.writel('.386')
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
    
    cb.writel('start:\n')
    for operation in program.operations:
        assert len(OperationType) == 14, 'Unhandled members of `OperationType`'
        if operation.type == OperationType.PUSH_INT:
            assert isinstance(operation.operand, int), 'Error in tparser.py in `program_from_tokens` or tokenizer.py in `tokenize_src`'
            cb.writel('push eax')
            cb.writel('mov eax, %d' % operation.operand)
            cb.writel('push eax')
        if operation.type == OperationType.PUSH_BOOL:
            assert False, 'PUSH_BOOL'
        if operation.type == OperationType.PUSH_STR:
            assert False, 'PUSH_STR'
        elif operation.type == OperationType.OPEN_IF:
            cb.write('.if ')
            cb.indent += 1
        elif operation.type == OperationType.CLOSE_IF:
            indentation -= 1
            cb.write('\n.endif ')
        elif operation.type == OperationType.CHECK_STACK_SIZE:
            assert False, 'CHECK_STACK_SIZE'
        elif operation.type == OperationType.CHECK_STACK_SIZE_G:
            assert False, 'CHECK_STACK_SIZE_G'
        elif operation.type == OperationType.PLUS_STACK:
            assert False, 'PLUS_STACK'
        elif operation.type == OperationType.MULT_STACK:
            assert False, 'MULT_STACK'
        elif operation.type == OperationType.PRINT_TOP:
            #assert False, 'PRINT_TOP'
            pass
        elif operation.type == OperationType.SWAP_STACK:
            assert False, 'SWAP_STACK'
        elif operation.type == OperationType.EQUALS_STACK:
            assert False, 'EQUALS_STACK'
        elif operation.type == OperationType.GREATER_STACK:
            assert False, 'GREATER_STACK'
        elif operation.type == OperationType.LESS_STACK:
            assert False, 'LESS_STACK'

    cb.writel(';; Ends the program ;;')
    cb.writel('end start')

    with open(os.path.join(os.getcwd(), f'{outfile}.asm'), 'w') as out:
        out.write(cb.code_body)

    filepath = os.path.join(os.getcwd(), outfile)
    os.system(_BUILD_WIN10 % filepath)

    filepath = os.path.join(os.getcwd(), outfile.split('/')[-1])
    os.system(_LINK_WIN10 % filepath)
    os.system(_EXECUTE_WIN10 % filepath)
