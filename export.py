# Exports OperationType, Keyword, and Intrinsic from src.globals
import src.py.globals as glbs

EXPORTS: list [str] = [
    'OperationType',
    'Keyword',
    'Intrinsic',
]

with open('enums.txt', 'w') as f:
    for cls in EXPORTS:
        enum = getattr(glbs, cls)
        for ele in enum:
            f.write('%s\n' % str(ele).replace('.', '_'))
        f.write('\n')