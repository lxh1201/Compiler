import random
from Symbols import *

Action = ['action_add', 'action_mul', 'action_equal', 'action_func_start', 'action_func_end',
          'action_func_para', 'action_func', 'action_declare']
Semantic = []

__global_table = []
__func_table = []
__in_func = False
__func_record = []

def produce_tmp():
    tmp = chr(random.randint(ord('A'), ord('Z')))
    index = 0
    while True:
        index += 1
        if tmp + str(index) not in Name_table:
            Name_table.append(tmp + str(index))
            #__func_table.append([tmp + str(index), -1, -1, -1])
            return ['symbol', len(Name_table)-1]

def produce_binop():
    b = Semantic.pop()
    op = Semantic.pop()
    a = Semantic.pop()
    tmp = produce_tmp()
    Semantic.append(tmp)
    return [op, a, b, tmp]

def action_declare():
    name = Semantic.pop()[1]
    t = Semantic[-1][1]
    if __in_func:
        sym_table = __func_table
    else:
        sym_table = __global_table
    if sym_table != []:
        tmp = [i[0] for i in sym_table]
        if name in tmp:
            exit(-1)
    sym_table.append([name, t, None, 'v', None])
    Semantic.append(('symbol', len(sym_table)-1))

def action_func():
    entry = __global_table[Semantic[-2][1]]
    entry[3] = 'f'
    entry[4] = [0, -1, []]
    global __in_func, __func_record
    __in_func = True
    __func_record = []

def action_func_para():
    print Semantic
    name = Semantic.pop()[1]
    t = Semantic.pop()[1]



def parse_action(name):
    if name == 'action_declare':
        action_declare()
    elif name == 'action_func':
        action_func()
    elif name == 'action_func_para':
        action_func_para()

