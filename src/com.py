import os
from globals import *



def com_program_win10(program: Program, outfile: str):
    code_body: str = ''
    indentation: int = 0

    def indent():
        return ' ' * 4 * indentation

    for operation in program.operations:
        if operation.type == OperationType.OPEN_IF:
            code_body += indent() + '.if '
        elif operation.type == OperationType.CLOSE_IF:
            pass
        elif operation.type == OperationType.CHECK_STACK_SIZE:
            pass


# filename = 'hello.asm'
# filepath = os.path.join(os.getcwd(), filename)
# os.system(f'\\masm32\\bin\\ml /c /Zd /coff {filepath}')