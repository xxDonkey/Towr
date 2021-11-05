import os
from globals import *

def com_program_win10(program: Program, outfile: str):
    pass

filename = 'hello.asm'
filepath = os.path.join(os.getcwd(), filename)
os.system(f'\\masm32\\bin\\ml /c /Zd /coff {filepath}')