import os
from globals import *

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
    __com_program_win10(program, outfile)

def __com_program_win10(program: Program, outfile: str) -> None:
    cb: CodeBody = CodeBody()
    indentation: int = 0

    # print(program)

    cb.writel(';; Necessary initialization statements ;;')
    cb.writel('.386')
    cb.writel('.model flat, stdcall\n')

    cb.writel(';; Necessary include statments ;;')
    cb.writel('inclue /masm32/macros/macros.asm')
    cb.writel('inclue /masm32/include/kernel32.inc')
    cb.writel('inclue /masm32/include/msvcrt.inc')
    cb.writel('inclue /masm32/include/masm32.inc')
    cb.writel('incluelib /masm32/lib/kernel32')
    cb.writel('incluelib /masm32/lib/msvcrt')
    cb.writel('incluelib /masm32/lib/\n')

    cb.writel(';; Data initialization ;;')
    cb.writel('.data\n')

    cb.writel(';; Code body ;;')
    cb.writel('.code\n')

    for variable in program.vars:
        if variable.datatype == DataType.INT:
            cb.writel(f'{variable.name} dowrd {variable.value}')
        elif variable.datatype == DataType.BOOL:
            pass
        elif variable.datatype == DataType.PTR:
            pass
    
    cb.writel('start:')
    for operation in program.operations:
        if operation.type == OperationType.OPEN_IF:
            cb.write('.if ')
            cb.indent += 1
        elif operation.type == OperationType.CLOSE_IF:
            indentation -= 1
            cb.write('\n.endif ')
        elif operation.type == OperationType.CHECK_STACK_SIZE:
            pass

    with open(os.path.join(os.getcwd(), f'{outfile}.asm'), 'w') as out:
        out.write(cb.code_body)

    cb.writel(';; Ends the program ;;')
    cb.writel('end start')


# filename = 'test'
# filepath = os.path.join(os.getcwd(), filename)
# os.system(_BUILD_WIN10 % filepath)
# os.system(_LINK_WIN10 % filepath)
# os.system(_EXECUTE_WIN10 % filepath)
